"""
Video transcription using Whisper + ffmpeg.

Extracts audio from video, then transcribes using OpenAI Whisper (local).
Supports timestamp extraction for time-indexed notes.
"""

import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def check_dependencies() -> dict:
    """Check if ffmpeg and whisper are installed.

    Returns:
        Dict with 'ffmpeg' and 'whisper' keys, values are paths or None.
    """
    result = {}
    for cmd in ["ffmpeg", "whisper"]:
        try:
            out = subprocess.run(
                ["which", cmd], capture_output=True, text=True, timeout=5
            )
            result[cmd] = out.stdout.strip() if out.returncode == 0 else None
        except Exception:
            result[cmd] = None
    return result


def get_video_duration(video_path: str) -> int:
    """Get video duration in seconds using ffprobe.

    Returns:
        Duration in seconds, or 0 if unable to determine.
    """
    try:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return int(float(data.get("format", {}).get("duration", 0)))
    except Exception as e:
        logger.warning("Could not get video duration: %s", e)
    return 0


def extract_audio(video_path: str, output_path: str = None) -> str:
    """Extract audio from video file using ffmpeg.

    Args:
        video_path: Path to the video file.
        output_path: Optional output path. Defaults to temp file.

    Returns:
        Path to the extracted audio WAV file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), "vtb_audio.wav")

    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",                    # No video
        "-acodec", "pcm_s16le",   # WAV format
        "-ar", "16000",           # 16kHz sample rate (optimal for Whisper)
        output_path,
        "-y",                     # Overwrite
    ]

    logger.info("Extracting audio: %s → %s", video_path, output_path)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    if not os.path.exists(output_path):
        raise RuntimeError(f"ffmpeg completed but output not found: {output_path}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logger.info("Audio extracted: %.1f MB", size_mb)
    return output_path


def transcribe(
    audio_path: str,
    language: str = None,
    model: str = "turbo",
    output_dir: str = None,
    initial_prompt: str = None,
) -> str:
    """Transcribe audio using Whisper (text only).

    Args:
        audio_path: Path to audio file (WAV recommended).
        language: Language code ('zh', 'en', etc). None for auto-detect.
        model: Whisper model name. 'turbo' recommended for speed+quality.
        output_dir: Directory for Whisper output files.
        initial_prompt: Optional hint for Whisper (e.g. "以下是中文内容").

    Returns:
        Transcribed text as a string.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), "vtb_whisper_output")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "whisper", audio_path,
        "--model", model,
        "--output_format", "txt",
        "--output_dir", output_dir,
    ]

    if language:
        cmd.extend(["--language", language])
    if initial_prompt:
        cmd.extend(["--initial_prompt", initial_prompt])

    logger.info("Transcribing with Whisper (model=%s, language=%s)", model, language or "auto")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    if result.returncode != 0:
        raise RuntimeError(f"Whisper failed: {result.stderr}")

    # Find the output text file
    audio_name = Path(audio_path).stem
    txt_path = os.path.join(output_dir, f"{audio_name}.txt")

    if not os.path.exists(txt_path):
        raise RuntimeError(f"Whisper output not found: {txt_path}")

    text = Path(txt_path).read_text(encoding="utf-8").strip()
    logger.info("Transcription complete: %d characters", len(text))
    return text


def transcribe_with_timestamps(
    audio_path: str,
    language: str = None,
    model: str = "turbo",
    output_dir: str = None,
    initial_prompt: str = None,
    interval_seconds: int = 60,
) -> tuple:
    """Transcribe audio with timestamp markers.

    Args:
        audio_path: Path to audio file.
        language: Language code or None for auto-detect.
        model: Whisper model name.
        output_dir: Directory for output files.
        initial_prompt: Optional hint for Whisper.
        interval_seconds: Seconds between timestamp markers (default: 60).

    Returns:
        Tuple of (full_text, timestamps_list).
        timestamps_list: [{"time": "01:30", "text": "段落开头..."}, ...]
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), "vtb_whisper_output")
    os.makedirs(output_dir, exist_ok=True)

    # Use SRT format to get timestamps
    cmd = [
        "whisper", audio_path,
        "--model", model,
        "--output_format", "srt",
        "--output_dir", output_dir,
    ]

    if language:
        cmd.extend(["--language", language])
    if initial_prompt:
        cmd.extend(["--initial_prompt", initial_prompt])

    logger.info("Transcribing with timestamps (model=%s)", model)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

    if result.returncode != 0:
        raise RuntimeError(f"Whisper failed: {result.stderr}")

    audio_name = Path(audio_path).stem
    srt_path = os.path.join(output_dir, f"{audio_name}.srt")

    if not os.path.exists(srt_path):
        # Fallback to plain text
        logger.warning("SRT not found, falling back to plain text")
        text = transcribe(audio_path, language, model, output_dir, initial_prompt)
        return text, []

    # Parse SRT file
    srt_content = Path(srt_path).read_text(encoding="utf-8")
    segments = _parse_srt(srt_content)

    # Build full text
    full_text = " ".join(seg["text"] for seg in segments)

    # Build timestamp markers at intervals
    timestamps = []
    last_marker = -interval_seconds  # Ensure first segment gets a marker

    for seg in segments:
        if seg["start_seconds"] - last_marker >= interval_seconds:
            timestamps.append({
                "time": _format_time(seg["start_seconds"]),
                "text": seg["text"][:80] + ("..." if len(seg["text"]) > 80 else ""),
            })
            last_marker = seg["start_seconds"]

    logger.info("Transcription complete: %d chars, %d timestamp markers", len(full_text), len(timestamps))
    return full_text, timestamps


def _parse_srt(srt_text: str) -> list:
    """Parse SRT subtitle format into segments.

    Returns:
        List of {"start_seconds": float, "text": str}
    """
    segments = []
    blocks = re.split(r"\n\n+", srt_text.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # Line 2: timestamp (00:00:01,000 --> 00:00:05,000)
        time_match = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*\d{2}:\d{2}:\d{2}",
            lines[1],
        )
        if not time_match:
            continue

        h, m, s, ms = time_match.groups()
        start_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

        # Lines 3+: text
        text = " ".join(lines[2:]).strip()
        if text:
            segments.append({"start_seconds": start_seconds, "text": text})

    return segments


def _format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def video_to_text(
    video_path: str,
    language: str = None,
    model: str = "turbo",
    initial_prompt: str = None,
    keep_audio: bool = False,
    with_timestamps: bool = False,
    timestamp_interval: int = 60,
) -> object:
    """One-step: extract audio from video and transcribe.

    Args:
        video_path: Path to video file.
        language: Language code or None for auto-detect.
        model: Whisper model name.
        initial_prompt: Optional hint for Whisper.
        keep_audio: If True, don't delete the intermediate audio file.
        with_timestamps: If True, return timestamps too.
        timestamp_interval: Seconds between timestamp markers.

    Returns:
        If with_timestamps=False: transcribed text string.
        If with_timestamps=True: tuple of (text, timestamps, duration_seconds).
    """
    deps = check_dependencies()
    if not deps["ffmpeg"]:
        raise RuntimeError("ffmpeg not installed. Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
    if not deps["whisper"]:
        raise RuntimeError("whisper not installed. Install: pip install openai-whisper")

    # Get duration
    duration = get_video_duration(video_path)

    audio_path = extract_audio(video_path)
    try:
        if with_timestamps:
            text, timestamps = transcribe_with_timestamps(
                audio_path, language=language, model=model,
                initial_prompt=initial_prompt,
                interval_seconds=timestamp_interval,
            )
            return text, timestamps, duration
        else:
            text = transcribe(audio_path, language=language, model=model, initial_prompt=initial_prompt)
            return text
    finally:
        if not keep_audio and os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info("Cleaned up temp audio file")
