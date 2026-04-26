# 📹 video-to-brain

[![Tests](https://github.com/LunaAI519/video-to-brain/actions/workflows/test.yml/badge.svg)](https://github.com/LunaAI519/video-to-brain/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/LunaAI519/video-to-brain/branch/main/graph/badge.svg)](https://codecov.io/gh/LunaAI519/video-to-brain)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/LunaAI519/video-to-brain)](https://github.com/LunaAI519/video-to-brain/releases)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://github.com/LunaAI519/video-to-brain#-docker-一键部署推荐)
[![Twitter Follow](https://img.shields.io/twitter/follow/LunaAI519?style=social)](https://twitter.com/LunaAI519)

**手机发视频，AI 帮你做笔记。**

不是转文字。是真的帮你做笔记——提炼要点、摘金句、列行动项、自动分类存入 Obsidian。

> 🎯 Built by a non-coder using vibe coding. If I can build this, you can too.

```
┌──────────┐    ┌──────────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│ 📱 手机   │───▶│ 🤖 Telegram  │───▶│ 🎙️ AI   │───▶│ 🧠 智能   │───▶│ 📚 知识库 │
│ 发/转发   │    │  Bot 接收    │    │ 转文字   │    │ 分析笔记  │    │ Obsidian │
│ 视频     │    │ (最大2GB)    │    │(Whisper) │    │(LLM分析)  │    │ 自动分类  │
└──────────┘    └──────────────┘    └─────────┘    └──────────┘    └──────────┘
```

<!-- 🎬 GIF Demo — replace with your own screen recording -->
<p align="center">
  <img src="docs/demo/demo.gif" alt="video-to-brain demo" width="600">
  <br>
  <em>手机发视频 → 30秒后收到 AI 笔记 → 自动存入 Obsidian</em>
</p>

**📸 看看生成的笔记长什么样：** [学习笔记示例](docs/demo/sample-note-study.md) · [内容素材示例](docs/demo/sample-note-content.md)

---

## 🤔 Before vs After

**没有这个工具之前：**
```
看到一个好视频 → 想着回头整理 → 忘了 → 再也找不到
                                    ↑
                              90%的人卡在这里
```

**用了之后：**
```
看到好视频 → 转发给机器人 → 30秒后收到：
  ✅ 一句话总结
  ✅ 5个核心要点
  ✅ 金句摘录
  ✅ 行动项清单
  ✅ 自动存入 Obsidian，带时间戳
```

**你省下了什么？**
- 🕐 一个 30 分钟的视频，手动记笔记要 20 分钟。这个工具 2 分钟搞定。
- 🧠 不是转录文字——是理解内容后帮你整理出可用的笔记。
- 🔍 3 个月后搜"那个视频说的什么来着"——Obsidian 搜一下就找到了。

---

## ✨ 核心功能

### 🤖 AI 智能笔记（不只是转文字）

同一段视频，选不同的模板，得到完全不同的笔记：

**📚 学习模式** — 知识点 + 概念解析 + 延伸思考
```markdown
## 🔑 核心要点
1. RAG 检索增强生成的三个关键步骤：索引、检索、生成
2. 向量数据库选型：Pinecone 适合生产环境，Chroma 适合原型

## 📖 概念解析
- RAG (Retrieval-Augmented Generation): 让 AI 先搜索再回答...

## 🧠 延伸思考
- 如果结合知识图谱，RAG 的准确率能提升多少？
```

**🎙️ 会议模式** — 讨论要点 + 共识 + 待办事项
```markdown
## 🔑 核心要点
1. Q2 预算需要削减 15%，优先砍营销支出

## ✅ 达成共识
- 新产品推迟到 Q3 发布

## ✅ 行动项
- [ ] 张总下周提交修订版预算
- [ ] 产品组更新发布时间线
```

**✍️ 内容素材模式** — 爆款观点 + 推文草稿
```markdown
## 🔥 爆款观点
- 99% 的人都在用 AI 聊天，只有 1% 的人用 AI 赚钱

## 🐦 推文草稿
草稿 1:
> 你以为 AI 是聊天工具？别人已经用它年入百万了。差距不在工具，在脑子。
```

**📰 资讯模式** — 核心论点 + 关键数据 + 我的思考
```markdown
## 🔑 核心论点
1. 2025 年 AI Agent 市场规模将达到 500 亿美元

## 📊 关键数据
- GPT-4o 推理速度提升 3 倍，成本降低 50%

## 🧠 延伸思考
- 这对个人开发者意味着什么？
```

### ⏱️ 时间戳导航

笔记自动标记视频时间线，方便回看：

```markdown
## ⏱️ 时间线
- **`00:00`** 开场，今天讲三个关于 AI 创业的误区...
- **`03:25`** 第一个误区：以为必须会写代码...
- **`08:10`** 第二个误区：追求完美再发布...
- **`15:30`** 实操演示：用 vibe coding 30 分钟做一个工具...
```

### 🔓 突破 20MB 限制

```
普通方式（Bot API）:   手机 → Telegram → Bot API → ❌ 20MB 限制
video-to-brain:        手机 → Telegram → MTProto → ✅ 最大 2GB
```

一个 30 分钟的视频可能 200MB+。Telegram Bot API 只能下 20MB。我们用 Pyrogram MTProto 协议直接绕过这个限制。

### 📱 手机就能用

不用开电脑。手机看到好视频，转发给机器人就完事了。转发别人的视频也行。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- ffmpeg（音频提取）
- Whisper（语音转文字）
- Telegram Bot Token
- _(可选)_ Telegram API ID & Hash — 突破 20MB 限制
- _(可选)_ LLM API Key — 开启 AI 智能笔记

### 安装

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

### 配置

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 必填
TELEGRAM_BOT_TOKEN=your_token_here

# 可选：大视频支持
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# 可选：AI 智能笔记（支持 OpenAI / Claude / Ollama 等）
LLM_API_KEY=your_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# 用本地 Ollama（完全免费）:
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=llama3
# LLM_API_KEY=ollama

# 笔记保存路径
OBSIDIAN_VAULT=~/Documents/my-vault
```

**如何获取 Telegram API ID：**
1. 打开 https://my.telegram.org
2. 用手机号登录
3. 点 "API development tools"
4. 填 App 名字和描述
5. 拿到 API ID（数字）和 API Hash

### 一键启动

```bash
python bot.py
```

Bot 命令：
- `/start` — 查看状态
- `/help` — 使用说明
- `/template` — 切换笔记模板（学习/会议/资讯/素材/自动）
- `/vault <路径>` — 修改保存位置
- `/status` — 查看当前设置

### 三种运行档次

| | 基础版 | 标准版 | 完整版 |
|---|---|---|---|
| 转文字 | ✅ | ✅ | ✅ |
| 时间戳 | ✅ | ✅ | ✅ |
| 大视频(>20MB) | ❌ | ✅ | ✅ |
| AI 智能笔记 | ❌ | ❌ | ✅ |
| 需要配置 | Bot Token | + API ID/Hash | + LLM API Key |
| 费用 | 免费 | 免费 | LLM API 费用 |

### 作为 Python 库使用

```python
from src import video_to_text, generate_note
from src.ai_processor import analyze_transcript

# 转录 + 时间戳
text, timestamps, duration = video_to_text("video.mp4", with_timestamps=True)

# AI 分析
analysis = analyze_transcript(text, template="study")

# 生成笔记
note_path = generate_note(
    transcript=text,
    output_dir="~/Documents/my-vault/",
    ai_analysis=analysis,
    timestamps=timestamps,
    duration_seconds=duration,
)
```

---

## 🐳 Docker 一键部署（推荐）

不想折腾 ffmpeg、Whisper 安装？用 Docker：

```bash
# 1. 克隆 + 配置
git clone https://github.com/LunaAI519/video-to-brain.git
cd video-to-brain
cp .env.example .env
# 编辑 .env，填入你的 token

# 2. 一键启动
docker compose up -d

# 查看日志
docker compose logs -f
```

就这么简单。ffmpeg、Whisper 全部自动装好。

---

## 🔒 安全特性

- **访问控制** — `ALLOWED_USERS` 白名单，只有指定的人能用
- **频率限制** — `RATE_LIMIT` 防止滥用（默认 5 次/分钟）
- **密钥隔离** — 所有敏感信息走 `.env`，不进代码
- **安全策略** — [SECURITY.md](SECURITY.md) 定义了漏洞报告流程

```env
# .env 中配置白名单（强烈建议）
ALLOWED_USERS=123456789,987654321
RATE_LIMIT=5
```

---

## 📁 项目结构

```
video-to-brain/
├── src/
│   ├── __init__.py           # 包入口
│   ├── env_loader.py         # 环境变量加载（共享）
│   ├── large_download.py     # Pyrogram 大视频下载（突破20MB）
│   ├── transcriber.py        # ffmpeg + Whisper 转录 + 时间戳
│   ├── note_generator.py     # Obsidian 笔记生成（支持AI模板）
│   └── ai_processor.py       # LLM 智能分析（4种模板）
├── tests/                    # 测试套件
├── examples/
│   └── basic_usage.py        # 用法示例
├── docs/
│   └── telegram-setup.md     # Telegram 配置教程
├── bot.py                    # Telegram Bot 一键启动
├── Dockerfile                # Docker 镜像
├── docker-compose.yml        # Docker Compose 配置
├── .env.example              # 环境变量模板
├── requirements.txt          # Python 依赖
├── LICENSE                   # MIT 协议
└── README.md
```

---

## 💡 使用场景

| 场景 | 怎么用 | 推荐模板 |
|---|---|---|
| 📚 看到好的教学视频 | 转发给机器人 | 学习模式 |
| 🎙️ 会议/通话录音 | 直接发给机器人 | 会议模式 |
| 📰 播客/采访/资讯 | 转发过来 | 资讯模式 |
| ✍️ 找内容灵感 | 发视频，提取爆点 | 素材模式 |
| 📋 不确定什么类型 | 交给AI判断 | 自动模式 |

---

## 🤖 配合 Hermes 使用

这个项目最初是为 [Hermes](https://github.com/hermes-ai/hermes-agent) AI 助手开发的视频处理模块。

如果你在用 Hermes，这个功能已经内置：
1. 在 Telegram 上给 Hermes 发视频
2. 说"帮我转成笔记"
3. 自动转录 + AI分析 + 存入 Obsidian

---

## 🙋 FAQ

**Q: 我不会写代码，能用吗？**
A: 这个项目就是一个不会写代码的人做的。按安装教程一步步来就行。

**Q: AI 分析要花钱吗？**
A: 不配置 LLM 也能用（基础转录模式免费）。配置了 LLM，费用取决于你用的模型。gpt-4o-mini 很便宜，一个视频大概几分钱。也可以用 Ollama 跑本地模型，完全免费。

**Q: 转录准确吗？**
A: Whisper 的中英文质量很高。如果遇到专业术语不准，在 `.env` 里加 initial_prompt 提示。

**Q: 需要 GPU 吗？**
A: 不需要。turbo 模型在 CPU 上也能跑，10 分钟视频大约 2-3 分钟。有 GPU 会更快。

**Q: 支持什么视频格式？**
A: mp4, mov, avi, mkv, webm — ffmpeg 能处理的都行。

**Q: 转发别人的视频可以吗？**
A: 可以。转发过来的视频会自动标注来源。

**Q: 笔记能自动分类到 Obsidian 不同文件夹吗？**
A: 能。AI 会根据内容自动判断分类（学习→知识库，商业→商业文件夹等）。

---

## 🛣️ Roadmap

- [x] Whisper 本地转录
- [x] 突破 20MB 限制（MTProto）
- [x] AI 智能笔记（4 种模板）
- [x] 时间戳导航
- [x] 转发视频支持
- [x] 自动分类到 Obsidian 文件夹
- [ ] 批量处理（连续发多个视频排队处理）
- [ ] 语音消息支持
- [ ] Web UI（不用 Telegram 也能用）
- [ ] 多语言摘要（视频是英文，笔记出中文）

---

## 📄 License

MIT — 随便用，不用问。

---

## 🌟 关于

我是 Luna，金融管理层，零编程基础。

2025 年开始用 AI + vibe coding 做自己的工具。这是我的第一个开源项目。

**起因很简单：** 我在外面跑了一天，路上刷到好几个有价值的视频。想发给 AI 帮我整理笔记，结果 Telegram 有 20MB 限制，发不了。

这个问题困扰了我半天。然后我用 vibe coding 解决了。

**你不需要变成程序员。你只需要知道问题在哪。**

AI 负责怎么做。你负责做什么。

---

⭐ 如果觉得有用，给个 Star 吧！

[![Twitter Follow](https://img.shields.io/twitter/follow/LunaAI519?style=social)](https://twitter.com/LunaAI519)

---

## 📈 Star History

<a href="https://star-history.com/#LunaAI519/video-to-brain&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=LunaAI519/video-to-brain&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=LunaAI519/video-to-brain&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=LunaAI519/video-to-brain&type=Date" />
 </picture>
</a>
