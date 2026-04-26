"""
Video transcription using Whisper + ffmpeg.

Extracts audio from video, then transcribes using OpenAI Whisper (local).
"""

import logging
import os
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
    """Transcribe audio using Whisper.
    
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


def video_to_text(
    video_path: str,
    language: str = None,
    model: str = "turbo",
    initial_prompt: str = None,
    keep_audio: bool = False,
) -> str:
    """One-step: extract audio from video and transcribe.
    
    Args:
        video_path: Path to video file.
        language: Language code or None for auto-detect.
        model: Whisper model name.
        initial_prompt: Optional hint for Whisper.
        keep_audio: If True, don't delete the intermediate audio file.
        
    Returns:
        Transcribed text as a string.
    """
    deps = check_dependencies()
    if not deps["ffmpeg"]:
        raise RuntimeError("ffmpeg not installed. Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
    if not deps["whisper"]:
        raise RuntimeError("whisper not installed. Install: pip install openai-whisper")
    
    audio_path = extract_audio(video_path)
    try:
        text = transcribe(audio_path, language=language, model=model, initial_prompt=initial_prompt)
        return text
    finally:
        if not keep_audio and os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info("Cleaned up temp audio file")
