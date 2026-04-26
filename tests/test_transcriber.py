"""Tests for src/transcriber.py — subprocess-based functions."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.transcriber import (
    _format_time,
    _parse_srt,
    check_dependencies,
    extract_audio,
    get_video_duration,
    transcribe,
    transcribe_with_timestamps,
    video_to_text,
)


class TestCheckDependencies:
    """Tests for check_dependencies()."""

    @patch("subprocess.run")
    def test_both_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="/usr/bin/ffmpeg\n")
        result = check_dependencies()
        assert "ffmpeg" in result
        assert "whisper" in result

    @patch("subprocess.run")
    def test_ffmpeg_missing(self, mock_run):
        def side_effect(cmd, **kwargs):
            m = MagicMock()
            if cmd[1] == "ffmpeg":
                m.returncode = 1
                m.stdout = ""
            else:
                m.returncode = 0
                m.stdout = "/usr/bin/whisper"
            return m

        mock_run.side_effect = side_effect
        result = check_dependencies()
        assert result["ffmpeg"] is None
        assert result["whisper"] is not None

    @patch("subprocess.run", side_effect=Exception("boom"))
    def test_exception_returns_none(self, mock_run):
        result = check_dependencies()
        assert result["ffmpeg"] is None
        assert result["whisper"] is None


class TestGetVideoDuration:
    """Tests for get_video_duration()."""

    @patch("subprocess.run")
    def test_valid_duration(self, mock_run):
        import json

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"format": {"duration": "125.5"}}),
        )
        assert get_video_duration("video.mp4") == 125

    @patch("subprocess.run")
    def test_ffprobe_fails(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        assert get_video_duration("video.mp4") == 0

    @patch("subprocess.run", side_effect=Exception("timeout"))
    def test_exception_returns_zero(self, mock_run):
        assert get_video_duration("video.mp4") == 0

    @patch("subprocess.run")
    def test_missing_duration_field(self, mock_run):
        import json

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"format": {}}),
        )
        assert get_video_duration("video.mp4") == 0


class TestExtractAudio:
    """Tests for extract_audio()."""

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_audio("/nonexistent/video.mp4")

    @patch("subprocess.run")
    def test_ffmpeg_fails(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="codec error")
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with pytest.raises(RuntimeError, match="ffmpeg failed"):
                extract_audio(f.name)

    @patch("subprocess.run")
    @patch("os.path.exists", side_effect=lambda p: not p.endswith(".wav"))
    def test_output_not_created(self, mock_exists, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with pytest.raises((RuntimeError, FileNotFoundError)):
            extract_audio("/tmp/fake_exists.mp4", "/tmp/output.wav")

    @patch("os.path.getsize", return_value=5 * 1024 * 1024)
    @patch("subprocess.run")
    def test_success(self, mock_run, mock_size):
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.NamedTemporaryFile(suffix=".mp4") as vid:
            out_path = os.path.join(tempfile.gettempdir(), "test_audio.wav")
            # Create the expected output
            with open(out_path, "w") as f:
                f.write("fake audio")
            try:
                result = extract_audio(vid.name, out_path)
                assert result == out_path
            finally:
                if os.path.exists(out_path):
                    os.remove(out_path)


class TestTranscribe:
    """Tests for transcribe()."""

    def test_audio_not_found(self):
        with pytest.raises(FileNotFoundError):
            transcribe("/nonexistent/audio.wav")

    @patch("subprocess.run")
    def test_whisper_fails(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="model not found")
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            with pytest.raises(RuntimeError, match="Whisper failed"):
                transcribe(f.name)

    @patch("subprocess.run")
    def test_success_with_language(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            out_dir = tempfile.mkdtemp()
            txt_path = os.path.join(out_dir, os.path.splitext(os.path.basename(audio.name))[0] + ".txt")
            with open(txt_path, "w") as f:
                f.write("Hello world this is a test")
            result = transcribe(audio.name, language="en", output_dir=out_dir)
            assert result == "Hello world this is a test"
            # Verify language flag was passed
            call_args = mock_run.call_args[0][0]
            assert "--language" in call_args
            assert "en" in call_args

    @patch("subprocess.run")
    def test_with_initial_prompt(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            out_dir = tempfile.mkdtemp()
            txt_path = os.path.join(out_dir, os.path.splitext(os.path.basename(audio.name))[0] + ".txt")
            with open(txt_path, "w") as f:
                f.write("中文内容")
            result = transcribe(audio.name, initial_prompt="以下是中文内容", output_dir=out_dir)
            assert result == "中文内容"
            call_args = mock_run.call_args[0][0]
            assert "--initial_prompt" in call_args


class TestTranscribeWithTimestamps:
    """Tests for transcribe_with_timestamps()."""

    def test_audio_not_found(self):
        with pytest.raises(FileNotFoundError):
            transcribe_with_timestamps("/nonexistent/audio.wav")

    @patch("subprocess.run")
    def test_whisper_fails(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            with pytest.raises(RuntimeError, match="Whisper failed"):
                transcribe_with_timestamps(f.name)

    @patch("subprocess.run")
    def test_success_with_srt(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        srt_content = """1
00:00:01,000 --> 00:00:05,000
Hello this is the beginning

2
00:01:05,000 --> 00:01:10,000
Now we move to the next topic

3
00:02:30,000 --> 00:02:35,000
Final thoughts here
"""
        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            out_dir = tempfile.mkdtemp()
            srt_path = os.path.join(out_dir, os.path.splitext(os.path.basename(audio.name))[0] + ".srt")
            with open(srt_path, "w") as f:
                f.write(srt_content)
            text, timestamps = transcribe_with_timestamps(audio.name, output_dir=out_dir, interval_seconds=60)
            assert "Hello" in text
            assert "Final thoughts" in text
            assert len(timestamps) >= 2  # At least first and one at 1:05


class TestVideoToText:
    """Tests for video_to_text()."""

    @patch("src.transcriber.check_dependencies", return_value={"ffmpeg": None, "whisper": "/usr/bin/whisper"})
    def test_no_ffmpeg(self, mock_deps):
        with pytest.raises(RuntimeError, match="ffmpeg"):
            video_to_text("video.mp4")

    @patch("src.transcriber.check_dependencies", return_value={"ffmpeg": "/usr/bin/ffmpeg", "whisper": None})
    def test_no_whisper(self, mock_deps):
        with pytest.raises(RuntimeError, match="whisper"):
            video_to_text("video.mp4")

    @patch("src.transcriber.transcribe", return_value="Hello world")
    @patch("src.transcriber.extract_audio", return_value="/tmp/audio.wav")
    @patch("src.transcriber.get_video_duration", return_value=120)
    @patch("src.transcriber.check_dependencies", return_value={"ffmpeg": "/usr/bin/ffmpeg", "whisper": "/usr/bin/whisper"})
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_basic_mode(self, mock_rm, mock_exists, mock_deps, mock_dur, mock_extract, mock_transcribe):
        result = video_to_text("video.mp4")
        assert result == "Hello world"

    @patch("src.transcriber.transcribe_with_timestamps", return_value=("Hello world", [{"time": "00:00", "text": "Hello..."}]))
    @patch("src.transcriber.extract_audio", return_value="/tmp/audio.wav")
    @patch("src.transcriber.get_video_duration", return_value=300)
    @patch("src.transcriber.check_dependencies", return_value={"ffmpeg": "/usr/bin/ffmpeg", "whisper": "/usr/bin/whisper"})
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_with_timestamps(self, mock_rm, mock_exists, mock_deps, mock_dur, mock_extract, mock_transcribe):
        text, timestamps, duration = video_to_text("video.mp4", with_timestamps=True)
        assert text == "Hello world"
        assert len(timestamps) == 1
        assert duration == 300
