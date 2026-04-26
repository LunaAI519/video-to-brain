"""
video-to-brain: Send videos via Telegram → AI transcribes → Smart notes in Obsidian

Break Telegram's 20MB limit. Turn any video into AI-powered structured notes.
Built by a non-coder using vibe coding.
"""

__version__ = "0.3.0"

from .transcriber import video_to_text, check_dependencies, get_video_duration, transcribe_with_timestamps
from .note_generator import generate_note, get_obsidian_path
from .large_download import download_large_video, is_available, shutdown
from .ai_processor import analyze_transcript, get_template_names
from .env_loader import load_env

__all__ = [
    "video_to_text",
    "check_dependencies",
    "get_video_duration",
    "transcribe_with_timestamps",
    "generate_note",
    "get_obsidian_path",
    "download_large_video",
    "is_available",
    "shutdown",
    "analyze_transcript",
    "get_template_names",
    "load_env",
]
