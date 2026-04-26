"""Tests for handle_video — the main video processing handler."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token-for-testing")


def _make_video_update(file_size=5 * 1024 * 1024, mime_type=None, caption="", is_forwarded=False):
    """Helper to create a mock Update with video attachment."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345

    msg = AsyncMock()
    msg.reply_text = AsyncMock()
    msg.chat_id = 12345
    msg.message_id = 999
    msg.caption = caption

    video = MagicMock()
    video.file_size = file_size
    video.get_file = AsyncMock()

    if mime_type:
        msg.video = None
        msg.document = MagicMock()
        msg.document.mime_type = mime_type
        msg.document.file_size = file_size
        msg.document.get_file = video.get_file
    else:
        msg.video = video
        msg.document = None

    msg.forward_date = MagicMock() if is_forwarded else None
    msg.forward_from = None
    msg.forward_from_chat = None
    msg.forward_sender_name = "Someone" if is_forwarded else None

    update.message = msg
    return update


class TestHandleVideoAccessControl:
    """Test access control in handle_video."""

    @pytest.fixture(autouse=True)
    def setup_bot(self):
        """Import bot and clear whitelist for each test."""
        import bot

        self.bot = bot
        self.original_users = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS.clear()
        yield
        bot.ALLOWED_USERS.clear()
        bot.ALLOWED_USERS.update(self.original_users)

    @pytest.mark.asyncio
    async def test_unauthorized_user_blocked(self):
        """Should reject unauthorized users when whitelist is set."""
        self.bot.ALLOWED_USERS.add(99999)  # only user 99999 allowed
        update = _make_video_update()
        context = MagicMock()

        await self.bot.handle_video(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "没有使用权限" in text

    @pytest.mark.asyncio
    async def test_authorized_user_proceeds(self):
        """Authorized user should not be blocked at access control."""
        self.bot.ALLOWED_USERS.add(12345)
        update = _make_video_update()
        context = MagicMock()

        # It will fail later (no real video to download), but should pass access control
        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        with patch.object(self.bot, "video_to_text", side_effect=Exception("test stop")):
            await self.bot.handle_video(update, context)

        # Should not have the "no permission" message
        first_call_text = update.message.reply_text.call_args_list[0][0][0]
        assert "没有使用权限" not in first_call_text


class TestHandleVideoRateLimiting:
    """Test rate limiting in handle_video."""

    @pytest.fixture(autouse=True)
    def setup_bot(self):
        import bot

        self.bot = bot
        self.original_users = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS.clear()
        # Reset rate limit tracking
        bot._rate_tracker.clear()
        yield
        bot.ALLOWED_USERS.clear()
        bot.ALLOWED_USERS.update(self.original_users)
        bot._rate_tracker.clear()

    @pytest.mark.asyncio
    async def test_rate_limit_kicks_in(self):
        """Should block after exceeding rate limit."""
        # Fill up rate limit
        import time

        user_id = 12345
        now = time.time()
        self.bot._rate_tracker[user_id] = [now] * (self.bot.RATE_LIMIT + 1)

        update = _make_video_update()
        context = MagicMock()

        await self.bot.handle_video(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "请求太频繁" in text


class TestHandleVideoDocument:
    """Test document type filtering."""

    @pytest.fixture(autouse=True)
    def setup_bot(self):
        import bot

        self.bot = bot
        self.original_users = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS.clear()
        bot._rate_tracker.clear()
        yield
        bot.ALLOWED_USERS.clear()
        bot.ALLOWED_USERS.update(self.original_users)

    @pytest.mark.asyncio
    async def test_non_video_document_ignored(self):
        """Should silently return for non-video documents."""
        update = _make_video_update(mime_type="application/pdf")
        context = MagicMock()

        await self.bot.handle_video(update, context)

        # Only the "no permission" or no call should happen
        # Since whitelist is empty, user is authorized, but non-video doc should be ignored
        # reply_text should not be called (no status message)
        assert update.message.reply_text.call_count == 0

    @pytest.mark.asyncio
    async def test_video_document_accepted(self):
        """Should process video/* MIME type documents."""
        update = _make_video_update(mime_type="video/mp4")
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        with patch("bot.video_to_text") as mock_vtt:
            mock_vtt.return_value = ("转录文字内容足够长的文本", [], 60.0)
            with patch("bot.generate_note", return_value="/tmp/test.md"):
                with patch("bot.analyze_transcript", return_value={}):
                    file_obj = AsyncMock()
                    file_obj.download_to_drive = AsyncMock()
                    update.message.document.get_file.return_value = file_obj

                    await self.bot.handle_video(update, context)

        # Should have sent at least the status message
        assert update.message.reply_text.call_count >= 1


class TestHandleVideoProcessing:
    """Test the full processing pipeline."""

    @pytest.fixture(autouse=True)
    def setup_bot(self):
        import bot

        self.bot = bot
        self.original_users = bot.ALLOWED_USERS.copy()
        bot.ALLOWED_USERS.clear()
        bot._rate_tracker.clear()
        yield
        bot.ALLOWED_USERS.clear()
        bot.ALLOWED_USERS.update(self.original_users)

    @pytest.mark.asyncio
    async def test_empty_transcript_handled(self):
        """Should report when no speech detected."""
        update = _make_video_update()
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        file_obj = AsyncMock()
        file_obj.download_to_drive = AsyncMock()
        update.message.video.get_file.return_value = file_obj

        with patch("bot.video_to_text") as mock_vtt:
            mock_vtt.return_value = ("", [], 0.0)
            await self.bot.handle_video(update, context)

        # Should tell user no speech detected
        calls = [c[0][0] for c in status_msg.edit_text.call_args_list]
        assert any("没有检测到语音" in c for c in calls)

    @pytest.mark.asyncio
    async def test_successful_processing(self):
        """Should complete full pipeline and send result."""
        update = _make_video_update(caption="测试视频")
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        file_obj = AsyncMock()
        file_obj.download_to_drive = AsyncMock()
        update.message.video.get_file.return_value = file_obj

        ai_result = {"summary": "这是一个测试视频", "key_points": ["要点1", "要点2"], "tags": ["测试"]}

        with (
            patch(
                "bot.video_to_text",
                return_value=("这是测试转录文字，内容足够长", [{"text": "这是", "start": "00:00"}], 30.0),
            ),
            patch("bot.generate_note", return_value="/tmp/notes/test.md"),
            patch("bot.analyze_transcript", return_value=ai_result),
            patch("bot.LLM_API_KEY", "fake-key"),
            patch("os.remove"),
        ):
            await self.bot.handle_video(update, context)

        # Final message should contain success indicator
        last_call = status_msg.edit_text.call_args_list[-1][0][0]
        assert "✅" in last_call
        assert "搞定" in last_call

    @pytest.mark.asyncio
    async def test_processing_error_handled(self):
        """Should catch and report processing errors."""
        update = _make_video_update()
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        file_obj = AsyncMock()
        file_obj.download_to_drive = AsyncMock()
        update.message.video.get_file.return_value = file_obj

        with patch("bot.video_to_text", side_effect=RuntimeError("Whisper crashed")):
            await self.bot.handle_video(update, context)

        last_call = status_msg.edit_text.call_args_list[-1][0][0]
        assert "❌" in last_call
        assert "处理失败" in last_call

    @pytest.mark.asyncio
    async def test_large_video_without_mtproto(self):
        """Should reject large videos when large download not available."""
        update = _make_video_update(file_size=50 * 1024 * 1024)  # 50MB
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        with patch("bot.large_dl_available", return_value=False):
            await self.bot.handle_video(update, context)

        calls = [c[0][0] for c in status_msg.edit_text.call_args_list]
        assert any("太大" in c for c in calls)

    @pytest.mark.asyncio
    async def test_forwarded_video_tags(self):
        """Forwarded videos should get '转发' tag."""
        update = _make_video_update(is_forwarded=True)
        context = MagicMock()

        status_msg = AsyncMock()
        status_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = status_msg

        file_obj = AsyncMock()
        file_obj.download_to_drive = AsyncMock()
        update.message.video.get_file.return_value = file_obj

        with (
            patch("bot.video_to_text", return_value=("转发视频的转录文字足够长", [], 20.0)),
            patch("bot.generate_note", return_value="/tmp/notes/fwd.md") as mock_gen,
            patch("bot.analyze_transcript", return_value={}),
            patch("os.remove"),
        ):
            await self.bot.handle_video(update, context)

        # Check that generate_note was called with '转发' in tags
        call_kwargs = mock_gen.call_args
        tags = call_kwargs.kwargs.get("tags") or call_kwargs[1].get("tags", [])
        assert "转发" in tags
