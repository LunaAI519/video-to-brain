"""
AI-powered note generation from video transcripts.

Supports multiple LLM backends via OpenAI-compatible API.
Works with: OpenAI GPT, Anthropic Claude (via proxy), local models (Ollama), etc.

Set LLM_API_KEY and LLM_BASE_URL in .env to configure.
"""

import json
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

# --- LLM Configuration ---

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def _call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Call LLM via OpenAI-compatible API. Falls back gracefully if unavailable."""
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY not set — skipping AI processing")
        return ""

    try:
        import urllib.request

        url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
        payload = json.dumps({
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}",
        })

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return ""


# --- Note Templates ---

TEMPLATES = {
    "study": {
        "name": "📚 学习笔记",
        "name_en": "Study Notes",
        "icon": "📚",
        "prompt": """你是一个学习笔记助手。请分析以下视频转录文字，生成结构化学习笔记。

要求输出以下 JSON 格式（中文）：
{
  "summary": "一句话总结（30字以内）",
  "key_points": ["核心知识点1", "核心知识点2", ...],
  "key_quotes": ["值得记住的金句1", ...],
  "concepts": ["涉及的概念/术语及简要解释1", ...],
  "think_deeper": ["延伸思考问题1", ...],
  "action_items": ["学完可以做的事1", ...],
  "tags": ["标签1", "标签2", ...],
  "difficulty": "入门/进阶/高级",
  "category": "学习/商业/内容/默认"
}

只输出 JSON，不要其他文字。""",
    },
    "meeting": {
        "name": "🎙️ 会议纪要",
        "name_en": "Meeting Notes",
        "icon": "🎙️",
        "prompt": """你是一个会议纪要助手。请分析以下视频/录音转录文字，生成结构化会议纪要。

要求输出以下 JSON 格式（中文）：
{
  "summary": "一句话总结本次会议（30字以内）",
  "participants_topics": ["讨论主题1: 主要观点", "讨论主题2: 主要观点", ...],
  "decisions": ["达成的共识/决定1", ...],
  "key_quotes": ["重要发言摘录1", ...],
  "action_items": ["待办事项1（负责人，如能识别）", ...],
  "open_questions": ["待解决问题1", ...],
  "tags": ["标签1", "标签2", ...],
  "category": "商业"
}

只输出 JSON，不要其他文字。""",
    },
    "news": {
        "name": "📰 资讯摘要",
        "name_en": "News/Podcast Brief",
        "icon": "📰",
        "prompt": """你是一个资讯分析助手。请分析以下视频/播客转录文字，提取核心信息。

要求输出以下 JSON 格式（中文）：
{
  "summary": "一句话总结（30字以内）",
  "core_arguments": ["核心论点1", "核心论点2", ...],
  "facts_data": ["提到的关键数据/事实1", ...],
  "key_quotes": ["值得引用的原话1", ...],
  "my_thoughts": ["可以从什么角度思考这个问题1", ...],
  "related_topics": ["相关话题/延伸阅读方向1", ...],
  "action_items": ["看完可以做的事1", ...],
  "tags": ["标签1", "标签2", ...],
  "category": "默认"
}

只输出 JSON，不要其他文字。""",
    },
    "content": {
        "name": "✍️ 内容素材",
        "name_en": "Content Material",
        "icon": "✍️",
        "prompt": """你是一个内容创作助手。请分析以下视频转录文字，提取可用于二次创作的素材。

要求输出以下 JSON 格式（中文）：
{
  "summary": "一句话总结视频核心观点（30字以内）",
  "hot_takes": ["可以直接发的爆款观点1", "爆款观点2", ...],
  "key_quotes": ["原文金句（可直接引用）1", ...],
  "content_angles": ["可以从这个角度写一篇: 角度描述1", ...],
  "tweet_drafts": ["可以发的推文草稿1（140字以内）", ...],
  "controversy": ["有争议的/能引发讨论的点1", ...],
  "action_items": ["可以产出的内容1", ...],
  "tags": ["标签1", "标签2", ...],
  "category": "内容"
}

只输出 JSON，不要其他文字。""",
    },
    "auto": {
        "name": "🤖 自动识别",
        "name_en": "Auto Detect",
        "icon": "🤖",
        "prompt": """你是一个智能笔记助手。请先判断这段转录文字的类型（学习/会议/资讯/内容素材），然后生成对应的结构化笔记。

要求输出以下 JSON 格式（中文）：
{
  "detected_type": "study/meeting/news/content",
  "summary": "一句话总结（30字以内）",
  "key_points": ["核心要点1", "核心要点2", ...],
  "key_quotes": ["值得记住的金句1", ...],
  "insights": ["深层洞察/延伸思考1", ...],
  "action_items": ["看完可以做的事1", ...],
  "tags": ["标签1", "标签2", ...],
  "category": "学习/商业/内容/默认"
}

只输出 JSON，不要其他文字。""",
    },
}


def analyze_transcript(
    transcript: str,
    template: str = "auto",
    custom_instruction: str = None,
) -> dict:
    """Use LLM to analyze transcript and generate structured notes.

    Args:
        transcript: The transcribed text.
        template: Template name ('study', 'meeting', 'news', 'content', 'auto').
        custom_instruction: Optional additional instruction for the LLM.

    Returns:
        Dict with structured note data, or empty dict if LLM unavailable.
    """
    if template not in TEMPLATES:
        template = "auto"

    tmpl = TEMPLATES[template]
    system_prompt = tmpl["prompt"]

    if custom_instruction:
        system_prompt += f"\n\n额外要求: {custom_instruction}"

    # Truncate very long transcripts to stay within token limits
    max_chars = 15000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n\n[... 转录文字过长，已截断 ...]"

    user_prompt = f"以下是视频转录文字：\n\n{transcript}"

    raw = _call_llm(system_prompt, user_prompt)
    if not raw:
        return {}

    # Parse JSON from response (handle markdown code blocks)
    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM JSON output: %s...", raw[:200])
        # Return raw text as fallback
        return {"raw_analysis": raw}


def get_template_names() -> dict:
    """Return template names for display."""
    return {k: v["name"] for k, v in TEMPLATES.items()}
