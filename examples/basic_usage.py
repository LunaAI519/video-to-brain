"""
video-to-brain 基础用法示例

展示三种使用方式：
1. 基础模式 — 只转文字，不需要 AI
2. AI 模式 — 自动生成智能笔记
3. 指定模板 — 不同视频用不同模板
"""

from src import generate_note, video_to_text
from src.ai_processor import analyze_transcript

# ============================================
# 例 1: 基础模式（只转文字，不需要 API）
# ============================================

text = video_to_text("path/to/video.mp4")

note_path = generate_note(
    transcript=text,
    title="这个视频讲了什么",
    tags=["学习", "AI"],
    output_dir="~/Documents/my-vault/01-收件箱/",
)
print(f"笔记已保存: {note_path}")


# ============================================
# 例 2: AI 智能模式（需要配置 LLM_API_KEY）
# ============================================

# 带时间戳的转录
text, timestamps, duration = video_to_text(
    "path/to/video.mp4",
    with_timestamps=True,
)

# AI 分析（自动检测内容类型）
analysis = analyze_transcript(text, template="auto")

# 生成智能笔记
note_path = generate_note(
    transcript=text,
    source="YouTube - 某某频道",
    output_dir="~/Documents/my-vault/",
    ai_analysis=analysis,  # AI 分析结果
    timestamps=timestamps,  # 时间戳
    duration_seconds=duration,  # 视频时长
)
print(f"AI 笔记已保存: {note_path}")
print(f"摘要: {analysis.get('summary', '无')}")
print(f"核心要点: {analysis.get('key_points', [])}")


# ============================================
# 例 3: 指定模板
# ============================================

# 学习视频 → 知识点 + 延伸思考
study_analysis = analyze_transcript(text, template="study")

# 会议录音 → 纪要 + 待办
meeting_analysis = analyze_transcript(text, template="meeting")

# 播客资讯 → 论点 + 数据
news_analysis = analyze_transcript(text, template="news")

# 内容素材 → 爆款观点 + 推文草稿
content_analysis = analyze_transcript(text, template="content")

# 生成笔记时传入对应的 analysis
note_path = generate_note(
    transcript=text,
    output_dir="~/Documents/my-vault/",
    ai_analysis=study_analysis,
    template="study",
)


# ============================================
# 例 4: 下载大视频（突破 20MB 限制）
# ============================================

import asyncio

from src import download_large_video, is_available


async def download_and_process():
    if is_available():
        path = await download_large_video(
            chat_id=-1001234567890,
            message_id=123,
            output_dir="./downloads/",
        )
        if path:
            text, timestamps, duration = video_to_text(path, with_timestamps=True)
            analysis = analyze_transcript(text)
            generate_note(
                transcript=text,
                output_dir="~/Documents/my-vault/",
                ai_analysis=analysis,
                timestamps=timestamps,
                duration_seconds=duration,
            )


asyncio.run(download_and_process())
