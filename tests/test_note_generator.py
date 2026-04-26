"""Tests for note_generator module."""

import os
import tempfile
import pytest
from src.note_generator import generate_note, get_obsidian_path, OBSIDIAN_FOLDERS


class TestGenerateNote:
    """Test generate_note function."""

    def test_basic_note_returns_content(self):
        """Basic note without output_dir returns string content."""
        result = generate_note(transcript="这是一段测试文字")
        assert isinstance(result, str)
        assert "这是一段测试文字" in result

    def test_basic_note_has_frontmatter(self):
        """Note should have YAML frontmatter."""
        result = generate_note(transcript="测试内容")
        assert result.startswith("---")
        assert "type: video-note" in result

    def test_custom_title(self):
        """Custom title should appear in note."""
        result = generate_note(transcript="内容", title="我的自定义标题")
        assert "我的自定义标题" in result

    def test_auto_title_from_transcript(self):
        """Without title, uses first line of transcript."""
        result = generate_note(transcript="这是视频的第一句话\n后面还有内容")
        assert "这是视频的第一句话" in result

    def test_custom_tags(self):
        """Custom tags should appear in note."""
        result = generate_note(transcript="内容", tags=["AI", "学习"])
        assert "#AI" in result
        assert "#学习" in result

    def test_default_tags(self):
        """Default tag should be 视频笔记."""
        result = generate_note(transcript="内容")
        assert "#视频笔记" in result

    def test_source_info(self):
        """Source should appear in note."""
        result = generate_note(transcript="内容", source="YouTube")
        assert "YouTube" in result

    def test_save_to_file(self):
        """Note should save to file when output_dir provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_note(
                transcript="测试保存到文件",
                title="测试笔记",
                output_dir=tmpdir,
            )
            assert os.path.exists(path)
            assert path.endswith(".md")
            content = open(path, encoding="utf-8").read()
            assert "测试保存到文件" in content

    def test_custom_filename(self):
        """Custom filename should be used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_note(
                transcript="内容",
                output_dir=tmpdir,
                filename="my-note.md",
            )
            assert path.endswith("my-note.md")

    def test_duration_display(self):
        """Duration should be formatted correctly."""
        result = generate_note(transcript="内容", duration_seconds=185)
        assert "3分5秒" in result

    def test_timestamps_section(self):
        """Timestamps should appear in note."""
        timestamps = [
            {"time": "00:00", "text": "开场白"},
            {"time": "03:25", "text": "核心内容开始"},
        ]
        result = generate_note(transcript="内容", timestamps=timestamps)
        assert "⏱️ 时间线" in result
        assert "00:00" in result
        assert "开场白" in result

    def test_ai_analysis_summary(self):
        """AI analysis summary should appear."""
        analysis = {
            "summary": "这是AI生成的摘要",
            "key_points": ["要点1", "要点2"],
            "tags": ["AI生成标签"],
        }
        result = generate_note(transcript="内容", ai_analysis=analysis)
        assert "这是AI生成的摘要" in result
        assert "要点1" in result
        assert "#AI生成标签" in result

    def test_ai_analysis_action_items(self):
        """AI action items should be checklists."""
        analysis = {
            "summary": "摘要",
            "action_items": ["做事情1", "做事情2"],
        }
        result = generate_note(transcript="内容", ai_analysis=analysis)
        assert "- [ ] 做事情1" in result

    def test_ai_analysis_quotes(self):
        """AI quotes should be blockquotes."""
        analysis = {
            "summary": "摘要",
            "key_quotes": ["这是一句金句"],
        }
        result = generate_note(transcript="内容", ai_analysis=analysis)
        assert "💬 这是一句金句" in result

    def test_ai_tags_merge_with_custom(self):
        """AI tags should merge with custom tags, no duplicates."""
        analysis = {
            "summary": "摘要",
            "tags": ["AI", "学习"],
        }
        result = generate_note(transcript="内容", tags=["AI", "自定义"], ai_analysis=analysis)
        # Should have all three unique tags
        assert "#AI" in result
        assert "#学习" in result
        assert "#自定义" in result

    def test_transcript_in_details_tag(self):
        """Full transcript should be in collapsible details tag."""
        result = generate_note(transcript="完整的转录文字在这里", ai_analysis={"summary": "摘要"})
        assert "<details>" in result
        assert "完整的转录文字在这里" in result

    def test_no_ai_basic_template(self):
        """Without AI, should show basic template."""
        result = generate_note(transcript="内容")
        assert "在这里添加你的笔记和想法" in result

    def test_footer_link(self):
        """Footer should have project link."""
        result = generate_note(transcript="内容")
        assert "video-to-brain" in result
        assert "github.com" in result


class TestGetObsidianPath:
    """Test get_obsidian_path function."""

    def test_default_category(self):
        path = get_obsidian_path("/vault", "默认")
        assert path == "/vault/01-收件箱"

    def test_study_category(self):
        path = get_obsidian_path("/vault", "学习")
        assert path == "/vault/30-知识库"

    def test_business_category(self):
        path = get_obsidian_path("/vault", "商业")
        assert path == "/vault/40-商业"

    def test_content_category(self):
        path = get_obsidian_path("/vault", "内容")
        assert path == "/vault/20-内容工厂"

    def test_unknown_falls_back(self):
        path = get_obsidian_path("/vault", "不存在的分类")
        assert path == "/vault/01-收件箱"

    def test_all_folders_defined(self):
        """All folder mappings should exist."""
        assert len(OBSIDIAN_FOLDERS) >= 4
