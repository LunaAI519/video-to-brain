"""
video-to-brain: Send videos via Telegram → AI transcribes → Save to Obsidian

Break Telegram's 20MB limit. Turn any video into structured notes.
Built by a non-coder using vibe coding.
"""

__version__ = "0.1.0"

from .transcriber import video_to_text, check_dependencies
from .note_generator import generate_note, get_obsidian_path
from .large_download import download_large_video, is_available, shutdown

__all__ = [
    "video_to_text",
    "check_dependencies",
    "generate_note",
    "get_obsidian_path",
    "download_large_video",
    "is_available",
    "shutdown",
]
