"""
基础用法示例 / Basic Usage Example

展示如何用 video-to-brain 将视频转成 Obsidian 笔记。
Shows how to use video-to-brain to turn videos into Obsidian notes.
"""

import sys
sys.path.insert(0, "..")

from src import video_to_text, generate_note, check_dependencies


def main():
    # 1. 检查依赖
    deps = check_dependencies()
    print(f"ffmpeg: {'✅' if deps['ffmpeg'] else '❌'} {deps['ffmpeg'] or 'Not installed'}")
    print(f"whisper: {'✅' if deps['whisper'] else '❌'} {deps['whisper'] or 'Not installed'}")
    
    if not all(deps.values()):
        print("\n请先安装缺失的依赖 / Please install missing dependencies first.")
        return
    
    # 2. 视频转文字（替换成你的视频路径）
    video_path = "path/to/your/video.mp4"
    print(f"\n正在处理视频: {video_path}")
    
    text = video_to_text(
        video_path,
        language=None,      # None = 自动检测语言
        model="turbo",      # turbo 最快，质量也够用
    )
    print(f"转录完成！{len(text)} 字符")
    print(f"预览: {text[:200]}...")
    
    # 3. 生成 Obsidian 笔记
    note_path = generate_note(
        transcript=text,
        title="我的视频笔记",
        source="Telegram",
        tags=["视频笔记", "AI"],
        output_dir="./output/",     # 替换成你的 Obsidian vault 路径
    )
    print(f"\n笔记已保存: {note_path}")


if __name__ == "__main__":
    main()
"""

# 异步用法（下载大视频） / Async usage (download large videos)

import asyncio
from src import download_large_video, is_available

async def download_example():
    if not is_available():
        print("Pyrogram not configured. Set TELEGRAM_API_ID and TELEGRAM_API_HASH.")
        return
    
    path = await download_large_video(
        chat_id=-1001234567890,     # 你的 chat ID
        message_id=123,             # 视频消息 ID
        output_dir="./downloads/",
    )
    
    if path:
        print(f"下载完成: {path}")
        # 然后可以用 video_to_text(path) 转录

# asyncio.run(download_example())
"""
