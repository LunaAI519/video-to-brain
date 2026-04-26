"""
Generate structured Obsidian notes from transcribed text.

Two modes:
  1. Basic mode — transcript only (no LLM needed)
  2. AI mode — LLM-powered structured notes with templates

For AI mode, set LLM_API_KEY in .env.
"""

import os
from datetime import datetime
from pathlib import Path


def _render_list(items: list, bullet: str = "-") -> str:
    """Render a list of items as markdown."""
    if not items:
        return f"{bullet} （无）\n"
    return "\n".join(f"{bullet} {item}" for item in items) + "\n"


def _render_checklist(items: list) -> str:
    """Render items as a markdown checklist."""
    if not items:
        return "- [ ] \n"
    return "\n".join(f"- [ ] {item}" for item in items) + "\n"


def _render_quotes(quotes: list) -> str:
    """Render quotes as blockquotes."""
    if not quotes:
        return ""
    return "\n".join(f"> 💬 {q}" for q in quotes) + "\n"


def generate_note(
    transcript: str,
    title: str = None,
    source: str = None,
    tags: list = None,
    output_dir: str = None,
    filename: str = None,
    ai_analysis: dict = None,
    template: str = "auto",
    timestamps: list = None,
    duration_seconds: int = None,
) -> str:
    """Generate a structured Obsidian-compatible markdown note.

    Args:
        transcript: The transcribed text from the video.
        title: Note title. Auto-generated if not provided.
        source: Video source (URL, author, etc).
        tags: List of tags (without #). AI may add more.
        output_dir: Directory to save the note. If None, returns content only.
        filename: Custom filename. Auto-generated if not provided.
        ai_analysis: Dict from ai_processor.analyze_transcript().
        template: Template used ('study', 'meeting', 'news', 'content', 'auto').
        timestamps: List of {"time": "MM:SS", "text": "..."} entries.
        duration_seconds: Video duration in seconds.

    Returns:
        Path to saved note, or note content if output_dir is None.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    # --- Build tags ---
    all_tags = list(tags or [])
    if ai_analysis and "tags" in ai_analysis:
        all_tags.extend(ai_analysis["tags"])
    if not all_tags:
        all_tags = ["视频笔记"]
    # Deduplicate
    all_tags = list(dict.fromkeys(all_tags))
    tag_str = " ".join(f"#{t}" for t in all_tags)

    # --- Title ---
    if ai_analysis and "summary" in ai_analysis and not title:
        title = ai_analysis["summary"]
    elif not title:
        first_line = transcript.split("\n")[0][:50].strip()
        title = first_line if first_line else "Untitled Video Note"

    # --- Duration ---
    duration_str = ""
    if duration_seconds:
        mins, secs = divmod(duration_seconds, 60)
        duration_str = f"{mins}分{secs}秒"

    # --- Template icon ---
    template_icons = {
        "study": "📚",
        "meeting": "🎙️",
        "news": "📰",
        "content": "✍️",
        "auto": "🤖",
    }
    icon = template_icons.get(template, "📝")

    # ========== Build Note ==========

    # Frontmatter (YAML)
    note_parts = []
    note_parts.append("---")
    note_parts.append(f'title: "{title}"')
    note_parts.append(f"date: {date_str}")
    note_parts.append("type: video-note")
    note_parts.append(f"template: {template}")
    note_parts.append(f"tags: [{', '.join(all_tags)}]")
    if source:
        note_parts.append(f'source: "{source}"')
    if duration_str:
        note_parts.append(f'duration: "{duration_str}"')
    note_parts.append(f"characters: {len(transcript)}")
    note_parts.append("---")
    note_parts.append("")

    # Title
    note_parts.append(f"# {icon} {title}")
    note_parts.append("")

    # Metadata line
    meta_items = [f"📅 {date_str} {time_str}"]
    if source:
        meta_items.append(f"📍 {source}")
    if duration_str:
        meta_items.append(f"⏱️ {duration_str}")
    meta_items.append(f"📊 {len(transcript)}字")
    note_parts.append(" · ".join(meta_items))
    note_parts.append(f"🏷️ {tag_str}")
    note_parts.append("")

    # --- AI Analysis Section ---
    if ai_analysis and not ai_analysis.get("raw_analysis"):
        note_parts.append("---")
        note_parts.append("")

        # One-line summary
        if "summary" in ai_analysis:
            note_parts.append(f"> **💡 一句话总结：{ai_analysis['summary']}**")
            note_parts.append("")

        # Key points / Core arguments
        points = (
            ai_analysis.get("key_points") or ai_analysis.get("core_arguments") or ai_analysis.get("participants_topics")
        )
        if points:
            note_parts.append("## 🔑 核心要点")
            note_parts.append("")
            for i, p in enumerate(points, 1):
                note_parts.append(f"**{i}.** {p}")
            note_parts.append("")

        # Hot takes (content template)
        if "hot_takes" in ai_analysis and ai_analysis["hot_takes"]:
            note_parts.append("## 🔥 爆款观点")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["hot_takes"]))

        # Decisions (meeting template)
        if "decisions" in ai_analysis and ai_analysis["decisions"]:
            note_parts.append("## ✅ 达成共识")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["decisions"]))

        # Key quotes
        if "key_quotes" in ai_analysis and ai_analysis["key_quotes"]:
            note_parts.append("## 💬 金句摘录")
            note_parts.append("")
            note_parts.append(_render_quotes(ai_analysis["key_quotes"]))

        # Facts & data (news template)
        if "facts_data" in ai_analysis and ai_analysis["facts_data"]:
            note_parts.append("## 📊 关键数据")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["facts_data"]))

        # Concepts (study template)
        if "concepts" in ai_analysis and ai_analysis["concepts"]:
            note_parts.append("## 📖 概念解析")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["concepts"]))

        # Insights / Think deeper
        insights = ai_analysis.get("insights") or ai_analysis.get("think_deeper") or ai_analysis.get("my_thoughts")
        if insights:
            note_parts.append("## 🧠 延伸思考")
            note_parts.append("")
            note_parts.append(_render_list(insights))

        # Tweet drafts (content template)
        if "tweet_drafts" in ai_analysis and ai_analysis["tweet_drafts"]:
            note_parts.append("## 🐦 推文草稿")
            note_parts.append("")
            for i, tweet in enumerate(ai_analysis["tweet_drafts"], 1):
                note_parts.append(f"**草稿 {i}:**")
                note_parts.append(f"> {tweet}")
                note_parts.append("")

        # Content angles
        if "content_angles" in ai_analysis and ai_analysis["content_angles"]:
            note_parts.append("## 🎯 创作角度")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["content_angles"]))

        # Controversy points
        if "controversy" in ai_analysis and ai_analysis["controversy"]:
            note_parts.append("## ⚡ 争议点")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["controversy"]))

        # Open questions (meeting template)
        if "open_questions" in ai_analysis and ai_analysis["open_questions"]:
            note_parts.append("## ❓ 待解决问题")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["open_questions"]))

        # Related topics
        if "related_topics" in ai_analysis and ai_analysis["related_topics"]:
            note_parts.append("## 🔗 相关话题")
            note_parts.append("")
            note_parts.append(_render_list(ai_analysis["related_topics"]))

        # Difficulty (study template)
        if "difficulty" in ai_analysis:
            note_parts.append(f"**难度**: {ai_analysis['difficulty']}")
            note_parts.append("")

        # Action items
        if "action_items" in ai_analysis and ai_analysis["action_items"]:
            note_parts.append("## ✅ 行动项")
            note_parts.append("")
            note_parts.append(_render_checklist(ai_analysis["action_items"]))

    elif ai_analysis and "raw_analysis" in ai_analysis:
        # Fallback: raw AI output
        note_parts.append("---")
        note_parts.append("")
        note_parts.append("## 🤖 AI 分析")
        note_parts.append("")
        note_parts.append(ai_analysis["raw_analysis"])
        note_parts.append("")

    else:
        # No AI — basic template
        note_parts.append("---")
        note_parts.append("")
        note_parts.append("## 📝 笔记")
        note_parts.append("")
        note_parts.append("> 💡 在这里添加你的笔记和想法")
        note_parts.append("")
        note_parts.append("## ✅ 行动项")
        note_parts.append("")
        note_parts.append("- [ ] ")
        note_parts.append("")

    # --- Timestamps Section ---
    if timestamps:
        note_parts.append("---")
        note_parts.append("")
        note_parts.append("## ⏱️ 时间线")
        note_parts.append("")
        for ts in timestamps:
            note_parts.append(f"- **`{ts['time']}`** {ts['text']}")
        note_parts.append("")

    # --- Full Transcript ---
    note_parts.append("---")
    note_parts.append("")
    note_parts.append("<details>")
    note_parts.append("<summary>📜 完整转录（点击展开）</summary>")
    note_parts.append("")
    note_parts.append(transcript)
    note_parts.append("")
    note_parts.append("</details>")
    note_parts.append("")

    # Footer
    note_parts.append("---")
    note_parts.append(
        "*Generated by [video-to-brain](https://github.com/LunaAI519/video-to-brain) — 手机发视频，AI变笔记*"
    )

    note = "\n".join(note_parts)

    # --- Save to file ---
    if output_dir:
        # Use AI-suggested category for folder routing
        if ai_analysis and "category" in ai_analysis:
            category = ai_analysis["category"]
            subfolder = OBSIDIAN_FOLDERS.get(category, "")
            if subfolder:
                output_dir = os.path.join(output_dir, subfolder)

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        if not filename:
            safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title)[:50]
            filename = f"{date_str}-{safe_title.strip()}.md"
        filepath = os.path.join(output_dir, filename)
        Path(filepath).write_text(note, encoding="utf-8")
        return filepath

    return note


# Pre-defined Obsidian folder mapping
OBSIDIAN_FOLDERS = {
    "学习": "30-知识库",
    "商业": "40-商业",
    "内容": "20-内容工厂",
    "默认": "01-收件箱",
}


def get_obsidian_path(vault_path: str, category: str = "默认") -> str:
    """Get the appropriate Obsidian folder for a category."""
    folder = OBSIDIAN_FOLDERS.get(category, OBSIDIAN_FOLDERS["默认"])
    return os.path.join(vault_path, folder)
