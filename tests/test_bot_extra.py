"""Additional bot.py tests for coverage — commands and handlers."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAccessControl:
    """Tests for _is_authorized and _check_rate_limit."""

    def test_no_whitelist_allows_all(self):
        from bot import _is_authorized

        # When ALLOWED_USERS is empty, all users are allowed
        import bot
        original = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS = set()
        assert _is_authorized(99999) is True
        bot.ALLOWED_USERS = original

    def test_whitelist_blocks_unauthorized(self):
        from bot import _is_authorized

        import bot
        original = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS = {111, 222}
        assert _is_authorized(333) is False
        assert _is_authorized(111) is True
        bot.ALLOWED_USERS = original

    def test_rate_limit_allows_within_limit(self):
        from bot import _check_rate_limit

        import bot
        original_limit = bot.RATE_LIMIT
        bot.RATE_LIMIT = 3
        bot._rate_tracker.clear()

        assert _check_rate_limit(100) is True
        assert _check_rate_limit(100) is True
        assert _check_rate_limit(100) is True
        assert _check_rate_limit(100) is False  # 4th should fail

        bot.RATE_LIMIT = original_limit
        bot._rate_tracker.clear()

    def test_rate_limit_window_expires(self):
        from bot import _check_rate_limit

        import bot
        original_limit = bot.RATE_LIMIT
        bot.RATE_LIMIT = 1
        bot._rate_tracker.clear()

        # Add an old timestamp (> 60s ago)
        bot._rate_tracker[200] = [time.time() - 120]
        assert _check_rate_limit(200) is True  # Old entries purged

        bot.RATE_LIMIT = original_limit
        bot._rate_tracker.clear()


class TestGetPrefs:
    """Tests for get_prefs."""

    def test_new_user_gets_defaults(self):
        from bot import get_prefs, user_prefs

        user_prefs.pop(99999, None)
        prefs = get_prefs(99999)
        assert prefs["template"] == "auto"
        assert prefs["queue"] == []
        user_prefs.pop(99999, None)

    def test_existing_user_returns_same(self):
        from bot import get_prefs, user_prefs

        user_prefs[88888] = {"template": "study", "queue": []}
        prefs = get_prefs(88888)
        assert prefs["template"] == "study"
        user_prefs.pop(88888, None)
