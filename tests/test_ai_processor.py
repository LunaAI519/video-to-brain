"""Tests for ai_processor module."""

import pytest
from src.ai_processor import TEMPLATES, get_template_names


class TestTemplates:
    """Test template definitions."""

    def test_all_templates_exist(self):
        """Should have all 5 templates."""
        expected = {"study", "meeting", "news", "content", "auto"}
        assert set(TEMPLATES.keys()) == expected

    def test_templates_have_required_fields(self):
        """Each template must have name, icon, and prompt."""
        for key, tmpl in TEMPLATES.items():
            assert "name" in tmpl, f"Template '{key}' missing 'name'"
            assert "icon" in tmpl, f"Template '{key}' missing 'icon'"
            assert "prompt" in tmpl, f"Template '{key}' missing 'prompt'"

    def test_prompts_request_json(self):
        """All prompts should ask for JSON output."""
        for key, tmpl in TEMPLATES.items():
            assert "JSON" in tmpl["prompt"], f"Template '{key}' prompt doesn't mention JSON"

    def test_prompts_request_summary(self):
        """All prompts should include summary field."""
        for key, tmpl in TEMPLATES.items():
            assert "summary" in tmpl["prompt"], f"Template '{key}' prompt missing 'summary'"

    def test_prompts_request_tags(self):
        """All prompts should include tags field."""
        for key, tmpl in TEMPLATES.items():
            assert "tags" in tmpl["prompt"], f"Template '{key}' prompt missing 'tags'"


class TestGetTemplateNames:
    """Test get_template_names function."""

    def test_returns_dict(self):
        result = get_template_names()
        assert isinstance(result, dict)

    def test_has_all_templates(self):
        result = get_template_names()
        assert len(result) == 5

    def test_names_are_strings(self):
        result = get_template_names()
        for k, v in result.items():
            assert isinstance(v, str)
            assert len(v) > 0
