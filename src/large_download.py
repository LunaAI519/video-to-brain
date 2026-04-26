"""
Pyrogram-based large video downloader for Telegram.

Telegram Bot API limits file downloads to 20 MB. This module uses
Pyrogram (MTProto protocol) to download files up to 2 GB.

Usage:
    from large_download import download_large_video, is_available

    if is_available():
        path = await download_large_video(chat_id, message_id, output_dir)
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-loaded singleton Pyrogram client
# ---------------------------------------------------------------------------

_client = None
_client_lock = asyncio.Lock()


def _load_credentials(env_path: str = None) -> tuple[int, str, str] | None:
    """Read TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN from env / .env."""
    # Ensure env vars are loaded (idempotent)
    from src.env_loader import load_env

    load_env(env_path or ".env")

    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not all([api_id, api_hash, bot_token]):
        return None

    try:
        return int(api_id), api_hash, bot_token
    except (ValueError, TypeError):
        logger.warning("Invalid TELEGRAM_API_ID: %s", api_id)
        return None


def is_available(env_path: str = None) -> bool:
    """Check if Pyrogram is importable and credentials are configured."""
    try:
        import pyrogram  # noqa: F401
    except ImportError:
        return False
    return _load_credentials(env_path) is not None


async def _get_client(env_path: str = None, session_dir: str = None):
    """Get or create the singleton Pyrogram bot client."""
    global _client
    async with _client_lock:
        if _client is not None and _client.is_connected:
            return _client

        creds = _load_credentials(env_path)
        if creds is None:
            raise RuntimeError(
                "Pyrogram credentials not configured. "
                "Set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN "
                "in your .env file or as environment variables."
            )

        api_id, api_hash, bot_token = creds

        from pyrogram import Client

        if session_dir is None:
            session_dir = os.path.expanduser("~/.video-to-brain/cache")
        os.makedirs(session_dir, exist_ok=True)

        # Use bot token auth — no user session needed
        _client = Client(
            name="video_to_brain",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            workdir=session_dir,
            no_updates=True,  # We only use this for downloads
        )

        await _client.start()
        logger.info("Pyrogram client started (bot mode)")
        return _client


async def download_large_video(
    chat_id: int,
    message_id: int,
    output_dir: str,
    env_path: str = None,
    session_dir: str = None,
) -> str | None:
    """Download a video from a Telegram message using Pyrogram MTProto.

    Args:
        chat_id: Telegram chat ID where the video was sent.
        message_id: Message ID of the video message.
        output_dir: Directory to save the downloaded video.
        env_path: Optional path to .env file with credentials.
        session_dir: Optional directory for Pyrogram session files.

    Returns:
        Local file path on success, None on failure.
    """
    try:
        client = await _get_client(env_path, session_dir)

        # Get the message
        msg = await client.get_messages(chat_id, message_id)
        if not msg or not (msg.video or msg.document or msg.animation):
            logger.warning("Message %s in %s has no downloadable media", message_id, chat_id)
            return None

        # Determine filename
        media = msg.video or msg.document or msg.animation
        file_name = getattr(media, "file_name", None) or f"video_{message_id}.mp4"

        # Ensure output dir exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_dir, file_name)

        # Avoid name collision
        if os.path.exists(output_path):
            base, ext = os.path.splitext(file_name)
            output_path = os.path.join(output_dir, f"{base}_{message_id}{ext}")

        file_size = getattr(media, "file_size", None)
        size_str = f"{file_size / 1024 / 1024:.1f} MB" if file_size else "unknown size"
        logger.info("Downloading %s to %s", size_str, output_path)

        # Download
        downloaded_path = await client.download_media(msg, file_name=output_path)

        if downloaded_path and os.path.exists(downloaded_path):
            size_mb = os.path.getsize(downloaded_path) / (1024 * 1024)
            logger.info("Download complete: %s (%.1f MB)", downloaded_path, size_mb)
            return str(downloaded_path)

        logger.warning("Download returned but file not found: %s", downloaded_path)
        return None

    except Exception as e:
        logger.error("Failed to download video: %s", e, exc_info=True)
        return None


async def shutdown():
    """Gracefully stop the Pyrogram client if running."""
    global _client
    if _client is not None:
        try:
            await _client.stop()
            logger.info("Pyrogram client stopped")
        except Exception:
            pass
        _client = None
