# 📹 video-to-brain

**手机发视频，AI变笔记。**

Send videos via Telegram → AI transcribes → Structured notes in Obsidian.

> 🎯 Built by a non-coder using vibe coding. If I can build this, you can too.

---

## ✨ 这是什么 / What is this

一个完整的视频转笔记工具链：

1. 📱 **手机发视频** — 通过 Telegram 机器人发送任意视频
2. 🔓 **突破 20MB 限制** — 用 Pyrogram MTProto 协议，最大支持 2GB
3. 🎙️ **AI 转文字** — Whisper 本地转录，支持中英文自动识别
4. 📝 **结构化笔记** — 自动整理成 Obsidian 格式的 Markdown 笔记
5. 💾 **存入知识库** — 一键保存到你的 Obsidian vault

A complete video-to-notes pipeline:

1. 📱 **Send video** — via Telegram bot, from your phone
2. 🔓 **Break 20MB limit** — Pyrogram MTProto protocol, supports up to 2GB
3. 🎙️ **AI transcription** — Local Whisper, auto-detects Chinese & English
4. 📝 **Structured notes** — Auto-formatted Obsidian-compatible Markdown
5. 💾 **Save to vault** — One-click save to your Obsidian knowledge base

---

## 🤔 为什么做这个 / Why

Telegram Bot API 有一个坑：**文件下载最大只能 20MB**。

对于视频来说，20MB 根本不够用。一个 5 分钟的视频就可能 100MB+。

我在外面跑了一天，想把路上看到的好视频随手甩给 AI 帮我整理笔记。结果卡在了 20MB 限制上。

花了半天用 vibe coding 解决了。

**我不会写代码。一行都不会。** 但我知道我要什么，AI 帮我实现。

---

## 🚀 快速开始 / Quick Start

### 环境要求 / Prerequisites

- Python 3.10+
- ffmpeg（音频提取）
- Whisper（语音转文字）
- Telegram Bot Token
- Telegram API ID & Hash（用于突破 20MB 限制）

### 安装 / Install

```bash
# 1. 克隆项目
git clone https://github.com/LunaAI519/video-to-brain.git
cd video-to-brain

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 ffmpeg
# macOS:
brew install ffmpeg
# Linux:
sudo apt install ffmpeg

# 4. 安装 Whisper
pip install openai-whisper
```

### 配置 / Configuration

创建 `.env` 文件：

```bash
cp .env.example .env
```

填入你的 Telegram 凭证：

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
```

**如何获取 API ID 和 Hash：**

1. 打开 https://my.telegram.org
2. 用手机号登录
3. 点 "API development tools"
4. 填 App 名字和描述
5. 获得 API ID（数字）和 API Hash（字母数字串）

### 使用 / Usage

```python
from src import video_to_text, generate_note

# 一步到位：视频转文字
text = video_to_text("path/to/video.mp4", language="zh")

# 生成 Obsidian 笔记
note_path = generate_note(
    transcript=text,
    title="这个视频讲了什么",
    tags=["学习", "AI"],
    output_dir="~/Documents/my-vault/01-收件箱/",
)
print(f"笔记已保存: {note_path}")
```

**下载大视频（突破 20MB 限制）：**

```python
import asyncio
from src import download_large_video, is_available

async def main():
    if is_available():
        path = await download_large_video(
            chat_id=-1001234567890,
            message_id=123,
            output_dir="./downloads/",
        )
        if path:
            text = video_to_text(path)
            print(text)

asyncio.run(main())
```

---

## 📁 项目结构 / Project Structure

```
video-to-brain/
├── src/
│   ├── __init__.py           # 包入口
│   ├── large_download.py     # Pyrogram 大视频下载（突破20MB限制）
│   ├── transcriber.py        # ffmpeg + Whisper 转录
│   └── note_generator.py     # Obsidian 笔记生成
├── examples/
│   └── basic_usage.py        # 基础用法示例
├── docs/
│   └── telegram-setup.md     # Telegram 配置详细教程
├── .env.example              # 环境变量模板
├── requirements.txt          # Python 依赖
├── LICENSE                   # MIT 协议
└── README.md                 # 你正在看的这个
```

---

## 🧠 核心原理 / How It Works

### 突破 20MB 限制

```
普通方式（Bot API）:   手机 → Telegram服务器 → Bot API → ❌ 20MB限制
我们的方式（MTProto）: 手机 → Telegram服务器 → Pyrogram MTProto → ✅ 最大2GB
```

Telegram Bot API 的 `getFile` 方法限制 20MB。但 Telegram 底层的 MTProto 协议没有这个限制。

我们用 [Pyrogram](https://docs.pyrogram.org/) 库直接走 MTProto 协议下载，绕过 Bot API 的限制。

### 转录流程

```
视频文件 → ffmpeg提取音频(WAV) → Whisper本地转录 → 文字 → Markdown笔记 → Obsidian
```

- **ffmpeg**: 从视频中提取音频，转为 16kHz WAV（Whisper 最优格式）
- **Whisper**: OpenAI 的语音识别模型，本地运行，支持 99 种语言
- **turbo 模型**: 速度最快，质量够用，推荐日常使用

---

## 💡 使用场景 / Use Cases

- 📚 **学习**: 看到好的教学视频，发给机器人自动变成笔记
- 🎙️ **会议**: 录音/录像自动转文字，再也不用手动记笔记
- 📰 **资讯**: 把采访、播客变成可搜索的文字档
- ✍️ **创作**: 视频内容自动提取要点，改编成文章/推文素材

---

## 🤖 配合 Hermes 使用 / Use with Hermes

这个项目最初是为 [Hermes](https://github.com/hermes-ai/hermes-agent) AI 助手开发的 Telegram 视频处理模块。

如果你在用 Hermes，这个功能已经内置在 `video-to-obsidian` skill 中，开箱即用：

1. 在 Telegram 上给 Hermes 发视频
2. 说"帮我转成笔记"
3. 自动转录 + 整理 + 存入 Obsidian

---

## 🙋 FAQ

**Q: 我不会写代码，能用吗？**
A: 这个项目就是一个不会写代码的人做的。按照安装教程一步步来就行。

**Q: 转录准确吗？**
A: Whisper 的中英文识别质量很高。如果遇到不准的情况，可以加 `initial_prompt` 提示。

**Q: 需要 GPU 吗？**
A: 不需要。turbo 模型在 CPU 上也能跑，10 分钟视频大概需要 2-3 分钟转录。

**Q: 支持什么视频格式？**
A: mp4, mov, avi, mkv, webm — ffmpeg 能处理的都行。

---

## 📄 License

MIT — 随便用，不用问。

---

## 🌟 关于作者 / About

我是 Luna，银行管理层，零编程基础。

用 AI + vibe coding 做出了自己的工具链。

这不是玩具，这是真的能改变你工作方式的东西。

**你不需要变成程序员。你需要变成那个最清楚问题在哪的人。**

AI 负责怎么做。你负责做什么。

---

⭐ 如果这个项目对你有帮助，给个 Star 吧！

[![Twitter Follow](https://img.shields.io/twitter/follow/LunaAI519?style=social)](https://twitter.com/LunaAI519)
