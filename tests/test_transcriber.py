"""Tests for transcriber module."""

import pytest

from src.transcriber import _format_time, _parse_srt


class TestParseSrt:
    """Test SRT parsing."""

    def test_basic_srt(self):
        srt = """1
00:00:01,000 --> 00:00:05,000
Hello world

2
00:00:06,000 --> 00:00:10,000
Second segment"""
        result = _parse_srt(srt)
        assert len(result) == 2
        assert result[0]["text"] == "Hello world"
        assert result[0]["start_seconds"] == pytest.approx(1.0)
        assert result[1]["text"] == "Second segment"

    def test_multiline_text(self):
        srt = """1
00:00:01,000 --> 00:00:05,000
First line
Second line"""
        result = _parse_srt(srt)
        assert len(result) == 1
        assert "First line" in result[0]["text"]
        assert "Second line" in result[0]["text"]

    def test_hour_timestamps(self):
        srt = """1
01:30:00,000 --> 01:30:05,000
After 1.5 hours"""
        result = _parse_srt(srt)
        assert result[0]["start_seconds"] == pytest.approx(5400.0)

    def test_empty_srt(self):
        result = _parse_srt("")
        assert result == []

    def test_malformed_srt(self):
        result = _parse_srt("not an srt file\njust random text")
        assert result == []


class TestFormatTime:
    """Test time formatting."""

    def test_seconds_only(self):
        assert _format_time(45) == "00:45"

    def test_minutes_and_seconds(self):
        assert _format_time(125) == "02:05"

    def test_hours(self):
        assert _format_time(3661) == "01:01:01"

    def test_zero(self):
        assert _format_time(0) == "00:00"

    def test_exact_minute(self):
        assert _format_time(60) == "01:00"

    def test_exact_hour(self):
        assert _format_time(3600) == "01:00:00"
