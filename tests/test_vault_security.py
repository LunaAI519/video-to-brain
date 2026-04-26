"""Tests for /vault command security — path traversal prevention."""

import os

import pytest

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token")


class TestVaultSecurity:
    """Ensure /vault command blocks dangerous paths."""

    @pytest.fixture(autouse=True)
    def allow_all_users(self):
        """Ensure no whitelist blocks our test user."""
        import bot

        original = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS.clear()
        yield
        bot.ALLOWED_USERS.clear()
        bot.ALLOWED_USERS.update(original)

    @pytest.mark.asyncio
    async def test_vault_blocks_etc(self, mock_update, mock_context):
        """Should block /etc as vault path."""
        from bot import set_vault

        mock_context.args = ["/etc/passwd"]
        await set_vault(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        call_text = mock_update.message.reply_text.call_args[0][0]
        assert "不允许" in call_text or "⛔" in call_text

    @pytest.mark.asyncio
    async def test_vault_blocks_proc(self, mock_update, mock_context):
        """Should block /proc as vault path."""
        from bot import set_vault

        mock_context.args = ["/proc/self"]
        await set_vault(mock_update, mock_context)
        call_text = mock_update.message.reply_text.call_args[0][0]
        assert "不允许" in call_text or "⛔" in call_text

    @pytest.mark.asyncio
    async def test_vault_blocks_traversal(self, mock_update, mock_context):
        """Should resolve and block path traversal attempts."""
        from bot import set_vault

        mock_context.args = ["/tmp/../etc/shadow"]
        await set_vault(mock_update, mock_context)
        call_text = mock_update.message.reply_text.call_args[0][0]
        assert "不允许" in call_text or "⛔" in call_text

    @pytest.mark.asyncio
    async def test_vault_allows_safe_path(self, mock_update, mock_context):
        """Should allow a normal home directory path."""
        import bot
        from bot import set_vault as sv

        original_vault = bot.OBSIDIAN_VAULT
        try:
            mock_context.args = ["/tmp/my-vault"]
            await sv(mock_update, mock_context)
            call_text = mock_update.message.reply_text.call_args[0][0]
            assert "已更改" in call_text
        finally:
            bot.OBSIDIAN_VAULT = original_vault

    @pytest.mark.asyncio
    async def test_vault_shows_current_when_no_args(self, mock_update, mock_context):
        """Should display current path when no args given."""
        from bot import set_vault

        mock_context.args = []
        await set_vault(mock_update, mock_context)
        call_text = mock_update.message.reply_text.call_args[0][0]
        assert "当前路径" in call_text
