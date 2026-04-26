"""Tests for bot module — command handlers and access control."""

import os

# Set env vars before importing bot
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token")


class TestAccessControl:
    """Test ALLOWED_USERS whitelist and rate limiting."""

    def test_is_authorized_no_whitelist(self):
        """When ALLOWED_USERS is empty, everyone is authorized."""
        from bot import ALLOWED_USERS, _is_authorized

        original = ALLOWED_USERS.copy()
        try:
            ALLOWED_USERS.clear()
            assert _is_authorized(12345) is True
            assert _is_authorized(99999) is True
        finally:
            ALLOWED_USERS.update(original)

    def test_is_authorized_with_whitelist(self):
        """When ALLOWED_USERS is set, only listed users are authorized."""
        import bot

        original = bot.ALLOWED_USERS.copy()
        try:
            bot.ALLOWED_USERS.clear()
            bot.ALLOWED_USERS.add(111)
            bot.ALLOWED_USERS.add(222)
            assert bot._is_authorized(111) is True
            assert bot._is_authorized(222) is True
            assert bot._is_authorized(333) is False
        finally:
            bot.ALLOWED_USERS.clear()
            bot.ALLOWED_USERS.update(original)

    def test_rate_limit_allows_under_limit(self):
        """Requests under limit should pass."""
        from bot import _check_rate_limit, _rate_tracker

        test_uid = 999001
        _rate_tracker.pop(test_uid, None)
        for _ in range(5):
            assert _check_rate_limit(test_uid) is True
        _rate_tracker.pop(test_uid, None)

    def test_rate_limit_blocks_over_limit(self):
        """Requests over limit should be blocked."""
        import bot

        test_uid = 999002
        bot._rate_tracker.pop(test_uid, None)
        original_limit = bot.RATE_LIMIT
        try:
            bot.RATE_LIMIT = 3
            assert bot._check_rate_limit(test_uid) is True
            assert bot._check_rate_limit(test_uid) is True
            assert bot._check_rate_limit(test_uid) is True
            assert bot._check_rate_limit(test_uid) is False  # 4th should fail
        finally:
            bot.RATE_LIMIT = original_limit
            bot._rate_tracker.pop(test_uid, None)


class TestGetPrefs:
    """Test user preference management."""

    def test_creates_default_prefs(self):
        """New user should get default prefs."""
        from bot import get_prefs, user_prefs

        test_id = 888001
        user_prefs.pop(test_id, None)
        prefs = get_prefs(test_id)
        assert prefs["template"] == "auto"
        assert prefs["queue"] == []
        user_prefs.pop(test_id, None)

    def test_returns_existing_prefs(self):
        """Existing user should get their stored prefs."""
        from bot import get_prefs, user_prefs

        test_id = 888002
        user_prefs[test_id] = {"template": "meeting", "queue": []}
        prefs = get_prefs(test_id)
        assert prefs["template"] == "meeting"
        user_prefs.pop(test_id, None)


class TestEnvLoader:
    """Test the shared env loader."""

    def test_load_env_from_file(self, tmp_path):
        """Should load env vars from a .env file."""
        from src.env_loader import load_env

        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VTB_VAR=hello_world\n# comment line\nBAD LINE\n")

        # Remove if already set
        os.environ.pop("TEST_VTB_VAR", None)
        load_env(str(env_file))
        assert os.environ.get("TEST_VTB_VAR") == "hello_world"
        os.environ.pop("TEST_VTB_VAR", None)

    def test_load_env_does_not_overwrite(self, tmp_path):
        """Should not overwrite existing env vars."""
        from src.env_loader import load_env

        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VTB_EXISTING=new_value\n")

        os.environ["TEST_VTB_EXISTING"] = "original"
        load_env(str(env_file))
        assert os.environ.get("TEST_VTB_EXISTING") == "original"
        os.environ.pop("TEST_VTB_EXISTING", None)

    def test_load_env_missing_file(self):
        """Should handle missing file gracefully."""
        from src.env_loader import load_env

        load_env("/nonexistent/.env")  # Should not raise
