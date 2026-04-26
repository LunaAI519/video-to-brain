"""Tests for _call_llm — LLM API calling with mocked HTTP."""

import json
import os
from unittest.mock import MagicMock, patch

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "fake-token")


class TestCallLLM:
    """Test the _call_llm function with mocked network calls."""

    def test_returns_empty_when_no_api_key(self):
        """Should return empty string when LLM_API_KEY is not set."""
        from src import ai_processor

        original_key = ai_processor.LLM_API_KEY
        try:
            ai_processor.LLM_API_KEY = ""
            result = ai_processor._call_llm("system", "user")
            assert result == ""
        finally:
            ai_processor.LLM_API_KEY = original_key

    @patch("urllib.request.urlopen")
    def test_successful_llm_call(self, mock_urlopen):
        """Should return LLM response content on success."""
        from src import ai_processor

        original_key = ai_processor.LLM_API_KEY
        try:
            ai_processor.LLM_API_KEY = "test-key-123"

            # Mock the HTTP response
            mock_response = MagicMock()
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_response.read.return_value = json.dumps(
                {"choices": [{"message": {"content": "  AI generated response  "}}]}
            ).encode("utf-8")
            mock_urlopen.return_value = mock_response

            result = ai_processor._call_llm("You are helpful.", "Hello!")
            assert result == "AI generated response"
            mock_urlopen.assert_called_once()
        finally:
            ai_processor.LLM_API_KEY = original_key

    @patch("urllib.request.urlopen")
    def test_llm_call_handles_network_error(self, mock_urlopen):
        """Should return empty string on network error."""
        from src import ai_processor

        original_key = ai_processor.LLM_API_KEY
        try:
            ai_processor.LLM_API_KEY = "test-key-123"
            mock_urlopen.side_effect = ConnectionError("Network down")

            result = ai_processor._call_llm("system", "user")
            assert result == ""
        finally:
            ai_processor.LLM_API_KEY = original_key

    @patch("urllib.request.urlopen")
    def test_llm_call_handles_malformed_response(self, mock_urlopen):
        """Should return empty string on malformed JSON response."""
        from src import ai_processor

        original_key = ai_processor.LLM_API_KEY
        try:
            ai_processor.LLM_API_KEY = "test-key-123"

            mock_response = MagicMock()
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_response.read.return_value = b"not json at all"
            mock_urlopen.return_value = mock_response

            result = ai_processor._call_llm("system", "user")
            assert result == ""
        finally:
            ai_processor.LLM_API_KEY = original_key
