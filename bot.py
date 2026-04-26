"""
video-to-brain Telegram Bot — 一键运行

发视频给机器人，AI 自动转文字 + 智能分析 + 生成 Obsidian 笔记。

用法:
    python bot.py

配置:
    在 .env 文件中设置必要的环境变量（见 .env.example）
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load .env file
def load_env(env_path=".env"):
    """Load environment variables from .env file."""
    if not os.path.exists(env_path):
        env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'\"")
                if key not in os.environ:
                    os.environ[key] = val

load_env()

# Now import after env is loaded
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes,
)

from src.transcriber import video_to_text, check_dependencies, get_video_duration
from src.note_generator import generate_note
from src.ai_processor import analyze_transcript, get_template_names, LLM_API_KEY
from src.large_download import is_available as large_dl_available

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("video-to-brain")

# Config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OBSIDIAN_VAULT = os.environ.get("OBSIDIAN_VAULT", os.path.expanduser("~/Documents/notes"))
MAX_BOT_API_SIZE = 20 * 1024 * 1024  # 20MB

# User preferences (per chat_id)
user_prefs = {}  # {chat_id: {"template": "auto", "queue": []}}


def get_prefs(chat_id: int) -> dict:
    """Get or create user preferences."""
    if chat_id not in user_prefs:
        user_prefs[chat_id] = {"template": "auto", "queue": []}
    return user_prefs[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    deps = check_dependencies()
    large_dl = large_dl_available()
    ai_ready = bool(LLM_API_KEY)

    status = f"""🧠 video-to-brain 已启动！

发视频给我，我帮你：
1. 🎙️ 转成文字（Whisper）
2. 🤖 AI 智能分析
3. 📝 生成结构化笔记
4. 💾 保存到 Obsidian

📁 笔记保存到: {OBSIDIAN_VAULT}

系统状态:
  ffmpeg: {'✅' if deps['ffmpeg'] else '❌ 未安装'}
  whisper: {'✅' if deps['whisper'] else '❌ 未安装'}
  大视频支持(>20MB): {'✅ 最大2GB' if large_dl else '❌ 仅支持20MB以下'}
  AI智能笔记: {'✅ 已配置' if ai_ready else '⚠️ 未配置（仅基础转录）'}

发送 /help 查看所有命令。"""

    await update.message.reply_text(status)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    templates = get_template_names()
    template_list = "\n".join(f"  {v}" for v in templates.values())

    help_text = f"""📖 使用说明

🎬 发视频: 直接发视频给我，自动处理
🗣️ 发语音: 发语音消息，同样处理
↩️ 转发视频: 从其他聊天转发视频过来也行

📋 笔记模板:
{template_list}

🔧 命令:
  /template — 选择笔记模板
  /vault <路径> — 修改笔记保存位置
  /status — 查看当前设置
  /help — 显示本帮助

💡 小技巧:
- 发视频时带上文字说明，会作为笔记标题
- 连续发多个视频，自动批量处理
- 转发别人的视频也可以处理"""

    await update.message.reply_text(help_text)


async def template_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /template command — show template selection buttons."""
    templates = get_template_names()
    prefs = get_prefs(update.effective_chat.id)
    current = prefs["template"]

    keyboard = []
    for key, name in templates.items():
        marker = " ← 当前" if key == current else ""
        keyboard.append([InlineKeyboardButton(f"{name}{marker}", callback_data=f"tpl_{key}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("选择笔记模板：", reply_markup=reply_markup)


async def template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle template selection button press."""
    query = update.callback_query
    await query.answer()

    template_key = query.data.replace("tpl_", "")
    templates = get_template_names()

    if template_key in templates:
        prefs = get_prefs(update.effective_chat.id)
        prefs["template"] = template_key
        await query.edit_message_text(f"✅ 模板已切换为: {templates[template_key]}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    prefs = get_prefs(update.effective_chat.id)
    templates = get_template_names()
    current_template = templates.get(prefs["template"], "未知")
    ai_ready = bool(LLM_API_KEY)

    text = f"""⚙️ 当前设置

📋 笔记模板: {current_template}
📁 保存路径: {OBSIDIAN_VAULT}
🤖 AI分析: {'✅ 开启' if ai_ready else '❌ 关闭'}
📹 大视频: {'✅ 支持' if large_dl_available() else '❌ 不支持'}"""

    await update.message.reply_text(text)


async def set_vault(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /vault command to change Obsidian vault path."""
    global OBSIDIAN_VAULT
    if context.args:
        new_path = " ".join(context.args)
        new_path = os.path.expanduser(new_path)
        OBSIDIAN_VAULT = new_path
        await update.message.reply_text(f"📁 笔记保存路径已更改为:\n{OBSIDIAN_VAULT}")
    else:
        await update.message.reply_text(f"📁 当前路径: {OBSIDIAN_VAULT}\n\n用法: /vault ~/Documents/my-vault")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming video messages (including forwarded videos)."""
    msg = update.message
    video = msg.video or msg.document

    if not video:
        return

    # Check if it's a video document
    if msg.document:
        mime = msg.document.mime_type or ""
        if not mime.startswith("video/"):
            return

    file_size = video.file_size or 0
    size_mb = file_size / (1024 * 1024)
    caption = msg.caption or ""

    # Detect forwarded video
    is_forwarded = msg.forward_date is not None
    source_info = "Telegram Video"
    if is_forwarded:
        if msg.forward_from:
            source_info = f"转发自 @{msg.forward_from.username or msg.forward_from.first_name}"
        elif msg.forward_from_chat:
            source_info = f"转发自 {msg.forward_from_chat.title or '频道'}"
        elif msg.forward_sender_name:
            source_info = f"转发自 {msg.forward_sender_name}"

    prefs = get_prefs(update.effective_chat.id)
    template = prefs["template"]

    # Status update
    templates = get_template_names()
    template_name = templates.get(template, "自动")
    status_msg = await msg.reply_text(
        f"📹 收到视频 ({size_mb:.1f} MB)\n"
        f"📋 模板: {template_name}\n"
        f"⏳ 正在处理..."
    )

    try:
        # Step 1: Download video
        if file_size > MAX_BOT_API_SIZE:
            if not large_dl_available():
                await status_msg.edit_text(
                    f"❌ 视频太大 ({size_mb:.1f} MB)，超过 20MB 限制。\n\n"
                    "请在 .env 中配置 TELEGRAM_API_ID 和 TELEGRAM_API_HASH\n"
                    "以启用大视频下载支持（最大 2GB）。"
                )
                return

            await status_msg.edit_text(
                f"📹 视频 {size_mb:.1f} MB\n⬇️ 正在通过 MTProto 下载大视频..."
            )

            from src.large_download import download_large_video
            cache_dir = os.path.expanduser("~/.video-to-brain/cache/videos")
            video_path = await download_large_video(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                output_dir=cache_dir,
            )

            if not video_path:
                await status_msg.edit_text("❌ 视频下载失败，请重试。")
                return
        else:
            await status_msg.edit_text(
                f"📹 视频 {size_mb:.1f} MB\n⬇️ 正在下载..."
            )

            file_obj = await video.get_file()
            cache_dir = os.path.expanduser("~/.video-to-brain/cache/videos")
            os.makedirs(cache_dir, exist_ok=True)
            video_path = os.path.join(cache_dir, f"video_{msg.message_id}.mp4")
            await file_obj.download_to_drive(video_path)

        # Step 2: Transcribe with timestamps
        await status_msg.edit_text("🎙️ 正在转文字（Whisper）...")

        result = video_to_text(video_path, with_timestamps=True)
        text, timestamps, duration = result

        if not text or len(text.strip()) < 10:
            await status_msg.edit_text("⚠️ 视频中没有检测到语音内容。")
            return

        # Step 3: AI analysis (if configured)
        ai_analysis = {}
        if LLM_API_KEY:
            await status_msg.edit_text("🤖 AI 正在分析内容...")
            ai_analysis = analyze_transcript(text, template=template)

        # Step 4: Generate note
        await status_msg.edit_text("📝 正在生成笔记...")

        title = caption if caption else None
        tags = ["视频笔记"]
        if is_forwarded:
            tags.append("转发")

        note_path = generate_note(
            transcript=text,
            title=title,
            source=source_info,
            tags=tags,
            output_dir=OBSIDIAN_VAULT,
            ai_analysis=ai_analysis,
            template=template,
            timestamps=timestamps,
            duration_seconds=duration,
        )

        # Step 5: Send result
        # Build summary
        summary = ""
        if ai_analysis and "summary" in ai_analysis:
            summary = f"\n💡 {ai_analysis['summary']}\n"

        key_points = ""
        points = ai_analysis.get("key_points") or ai_analysis.get("core_arguments") or []
        if points:
            key_points = "\n🔑 核心要点:\n" + "\n".join(f"  {i}. {p}" for i, p in enumerate(points[:5], 1)) + "\n"

        result_text = f"""✅ 搞定！
{summary}{key_points}
📝 笔记: {os.path.basename(note_path)}
📁 位置: {os.path.dirname(note_path)}
📊 转录: {len(text)} 字 · {'AI分析 ✅' if ai_analysis else '基础模式'}
⏱️ 时间标记: {len(timestamps)} 个"""

        if len(result_text) > 4000:
            result_text = result_text[:4000] + "..."

        await status_msg.edit_text(result_text)

        # Clean up video file
        try:
            os.remove(video_path)
        except Exception:
            pass

    except Exception as e:
        logger.error("Error processing video: %s", e, exc_info=True)
        await status_msg.edit_text(f"❌ 处理失败: {str(e)[:200]}")


def main():
    """Start the bot."""
    if not BOT_TOKEN:
        print("❌ 请设置 TELEGRAM_BOT_TOKEN")
        print("   在 .env 文件中添加: TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)

    # Check dependencies
    deps = check_dependencies()
    if not deps["ffmpeg"]:
        print("⚠️  ffmpeg 未安装: brew install ffmpeg (macOS) 或 apt install ffmpeg (Linux)")
    if not deps["whisper"]:
        print("⚠️  whisper 未安装: pip install openai-whisper")

    if not all(deps.values()):
        print("\n请先安装缺失的依赖再启动。")
        sys.exit(1)

    ai_ready = bool(LLM_API_KEY)

    print("🧠 video-to-brain bot 启动中...")
    print(f"📁 笔记保存到: {OBSIDIAN_VAULT}")
    print(f"📹 大视频支持: {'✅ 已启用' if large_dl_available() else '❌ 未配置'}")
    print(f"🤖 AI智能笔记: {'✅ 已启用' if ai_ready else '⚠️ 未配置（仅基础转录）'}")
    print()

    # Create Obsidian vault dir if needed
    os.makedirs(OBSIDIAN_VAULT, exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("vault", set_vault))
    app.add_handler(CommandHandler("template", template_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(template_callback, pattern=r"^tpl_"))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("✅ Bot 已启动！在 Telegram 上发视频试试。")
    print("   按 Ctrl+C 停止。\n")

    app.run_polling()


if __name__ == "__main__":
    main()
