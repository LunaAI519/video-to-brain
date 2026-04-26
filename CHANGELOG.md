# 📋 Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-04-26

### 🔒 Security & Access Control
- `ALLOWED_USERS` whitelist — restrict who can use the bot
- Rate limiting (`RATE_LIMIT`) — prevent abuse (default 5 req/min)
- Access control shown in `/status` command

### 🐳 Docker
- `Dockerfile` for one-command deployment (ffmpeg + Whisper pre-installed)
- `docker-compose.yml` with volume mounts for vault and cache
- `.dockerignore` for clean builds

### 🧪 Testing & CI
- Bot command tests with mocking (access control, rate limiting, prefs)
- `env_loader` module tests
- Coverage reporting with `pytest-cov`
- Codecov integration in CI
- Dependabot for pip and GitHub Actions auto-updates

### 🔧 Code Quality
- Extracted shared `src/env_loader.py` (removed duplicate `.env` parsing)
- Simplified `large_download.py` credentials loading
- Enhanced `/help` command with full command reference

### 📖 Documentation
- README: Docker deployment section
- README: Security features section
- README: Star History chart
- README: Codecov and Docker badges
- README: GIF demo placeholder
- Updated `.env.example` with `ALLOWED_USERS` and `RATE_LIMIT`
- Updated project structure in README

### 🚀 CI/CD
- Auto-release workflow (tag push → GitHub Release with changelog)

## [0.2.0] - 2026-04-26

### 🤖 AI Smart Notes
- LLM-powered analysis: auto-generates summary, key points, quotes, action items
- 4 note templates: study, meeting, news/podcast, content material
- Auto-detect mode: AI picks the best template based on content
- Supports any OpenAI-compatible API (GPT, Claude, Ollama, etc.)
- Graceful degradation: works without LLM (basic transcription mode)

### ⏱️ Timestamps
- Time-indexed markers in notes (every 60 seconds)
- SRT parsing from Whisper output
- Video duration detection via ffprobe

### 📱 Bot Upgrades
- `/template` command with inline buttons for template selection
- `/status` command to view current settings
- Forwarded video support with automatic source attribution
- Improved progress messages during processing

### 📝 Note Generator
- YAML frontmatter for Obsidian metadata
- Collapsible full transcript (HTML details tag)
- AI-powered auto-categorization into Obsidian folders
- Rich formatting: numbered points, blockquotes, checklists

### 📖 Documentation
- Complete README rewrite with Before/After comparison
- Three-tier setup guide (basic / standard / full)
- Use case table with recommended templates
- FAQ section

## [0.1.0] - 2026-04-25

### 🎉 Initial Release
- Telegram Bot with video processing
- Whisper local transcription (Chinese & English auto-detect)
- Break Telegram 20MB limit via Pyrogram MTProto (up to 2GB)
- Basic Obsidian note generation
- ffmpeg audio extraction
