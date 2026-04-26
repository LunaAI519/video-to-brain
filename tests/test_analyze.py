"""Tests for analyze_transcript — JSON parsing and template selection."""

import json
import os
from unittest.mock import patch

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token-for-testing")

from src.ai_processor import TEMPLATES, analyze_transcript


class TestAnalyzeTranscript:
    """Test analyze_transcript function."""

    def test_unknown_template_falls_back_to_auto(self):
        """Unknown template should fall back to 'auto'."""
        with patch("src.ai_processor._call_llm", return_value='{"summary": "test"}') as mock:
            analyze_transcript("test text", template="nonexistent")
            # Should use auto template's prompt
            call_args = mock.call_args[0]
            assert TEMPLATES["auto"]["prompt"] in call_args[0]

    def test_valid_json_response_parsed(self):
        """Should parse valid JSON from LLM response."""
        fake_response = json.dumps({"summary": "测试摘要", "tags": ["AI"]})
        with patch("src.ai_processor._call_llm", return_value=fake_response):
            result = analyze_transcript("test transcript")
            assert result["summary"] == "测试摘要"
            assert "AI" in result["tags"]

    def test_json_in_markdown_code_block(self):
        """Should handle JSON wrapped in ```json ... ``` blocks."""
        fake_response = '```json\n{"summary": "markdown wrapped"}\n```'
        with patch("src.ai_processor._call_llm", return_value=fake_response):
            result = analyze_transcript("test")
            assert result["summary"] == "markdown wrapped"

    def test_empty_llm_response_returns_empty_dict(self):
        """Should return empty dict when LLM returns nothing."""
        with patch("src.ai_processor._call_llm", return_value=""):
            result = analyze_transcript("test")
            assert result == {}

    def test_malformed_json_returns_raw(self):
        """Should return raw text when JSON parsing fails."""
        with patch("src.ai_processor._call_llm", return_value="This is not JSON at all"):
            result = analyze_transcript("test")
            assert "raw_analysis" in result
            assert "not JSON" in result["raw_analysis"]

    def test_long_transcript_truncated(self):
        """Transcripts over 15000 chars should be truncated."""
        long_text = "A" * 20000
        with patch("src.ai_processor._call_llm", return_value='{"summary": "ok"}') as mock:
            analyze_transcript(long_text)
            user_prompt = mock.call_args[0][1]
            assert "截断" in user_prompt
            assert len(user_prompt) < 20000

    def test_custom_instruction_appended(self):
        """Custom instruction should be added to system prompt."""
        with patch("src.ai_processor._call_llm", return_value='{"summary": "ok"}') as mock:
            analyze_transcript("test", custom_instruction="请用英文回答")
            system_prompt = mock.call_args[0][0]
            assert "请用英文回答" in system_prompt

    def test_each_template_has_required_fields(self):
        """Every template should have name, icon, and prompt."""
        for key, tmpl in TEMPLATES.items():
            assert "name" in tmpl, f"Template '{key}' missing 'name'"
            assert "icon" in tmpl, f"Template '{key}' missing 'icon'"
            assert "prompt" in tmpl, f"Template '{key}' missing 'prompt'"
            assert len(tmpl["prompt"]) > 50, f"Template '{key}' prompt too short"

    def test_study_template_used(self):
        """Study template should use the study prompt."""
        with patch("src.ai_processor._call_llm", return_value='{"summary": "study"}') as mock:
            analyze_transcript("test", template="study")
            system_prompt = mock.call_args[0][0]
            assert "学习笔记" in system_prompt

    def test_meeting_template_used(self):
        """Meeting template should use the meeting prompt."""
        with patch("src.ai_processor._call_llm", return_value='{"summary": "meeting"}') as mock:
            analyze_transcript("test", template="meeting")
            system_prompt = mock.call_args[0][0]
            assert "会议" in system_prompt
