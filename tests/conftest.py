"""Shared test fixtures for video-to-brain."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure bot can be imported without a real token
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token-for-testing")


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    update.message.forward_date = None
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram CallbackContext."""
    context = MagicMock()
    context.args = []
    return context


@pytest.fixture
def sample_transcript():
    """A short sample transcript for testing."""
    return (
        "Hello everyone, welcome to the meeting.\n"
        "Today we'll discuss the quarterly results.\n"
        "Revenue is up 15% year over year.\n"
        "We need to focus on customer retention next quarter."
    )


@pytest.fixture
def sample_srt():
    """A sample SRT subtitle content."""
    return (
        "1\n"
        "00:00:00,000 --> 00:00:05,000\n"
        "Hello everyone, welcome.\n\n"
        "2\n"
        "00:00:05,000 --> 00:00:10,000\n"
        "Let's get started.\n\n"
    )
