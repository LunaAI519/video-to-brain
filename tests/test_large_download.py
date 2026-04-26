"""Tests for src/large_download.py — Pyrogram MTProto downloader."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.large_download import _load_credentials, is_available, shutdown


class TestLoadCredentials:
    """Tests for _load_credentials()."""

    @patch("src.env_loader.load_env")
    @patch.dict(os.environ, {
        "TELEGRAM_API_ID": "12345",
        "TELEGRAM_API_HASH": "abcdef",
        "TELEGRAM_BOT_TOKEN": "tok123",
    })
    def test_valid_credentials(self, mock_load):
        result = _load_credentials()
        assert result == (12345, "abcdef", "tok123")

    @patch("src.env_loader.load_env")
    @patch.dict(os.environ, {
        "TELEGRAM_API_ID": "",
        "TELEGRAM_API_HASH": "",
        "TELEGRAM_BOT_TOKEN": "",
    }, clear=True)
    def test_missing_credentials(self, mock_load):
        # Clear relevant env vars
        for k in ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_BOT_TOKEN"]:
            os.environ.pop(k, None)
        result = _load_credentials()
        assert result is None

    @patch("src.env_loader.load_env")
    @patch.dict(os.environ, {
        "TELEGRAM_API_ID": "not_a_number",
        "TELEGRAM_API_HASH": "abcdef",
        "TELEGRAM_BOT_TOKEN": "tok123",
    })
    def test_invalid_api_id(self, mock_load):
        result = _load_credentials()
        assert result is None

    @patch("src.env_loader.load_env")
    @patch.dict(os.environ, {
        "TELEGRAM_API_ID": "12345",
        "TELEGRAM_API_HASH": "abcdef",
        "TELEGRAM_BOT_TOKEN": "",
    })
    def test_partial_credentials(self, mock_load):
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        result = _load_credentials()
        assert result is None


class TestIsAvailable:
    """Tests for is_available()."""

    @patch("src.large_download._load_credentials", return_value=(123, "hash", "token"))
    @patch.dict("sys.modules", {"pyrogram": MagicMock()})
    def test_available_with_pyrogram(self, mock_creds):
        result = is_available()
        assert result is True

    @patch("src.large_download._load_credentials", return_value=None)
    def test_not_available_no_creds(self, mock_creds):
        result = is_available()
        assert result is False


class TestShutdown:
    """Tests for shutdown()."""

    @pytest.mark.asyncio
    async def test_shutdown_no_client(self):
        import src.large_download as ld

        ld._client = None
        await shutdown()
        assert ld._client is None

    @pytest.mark.asyncio
    async def test_shutdown_with_client(self):
        import src.large_download as ld

        mock_client = AsyncMock()
        ld._client = mock_client
        await shutdown()
        mock_client.stop.assert_called_once()
        assert ld._client is None

    @pytest.mark.asyncio
    async def test_shutdown_stop_raises(self):
        import src.large_download as ld

        mock_client = AsyncMock()
        mock_client.stop.side_effect = Exception("connection closed")
        ld._client = mock_client
        await shutdown()  # Should not raise
        assert ld._client is None
