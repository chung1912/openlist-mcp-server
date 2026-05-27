"""Tests for OpenList API client."""

from unittest import mock

import pytest
from httpx import Response

from openlist_mcp.client import OpenListClient, OpenListError, get_client


class TestOpenListError:
    """Test cases for OpenListError."""

    def test_error_with_code(self) -> None:
        """Test error with status code."""
        error = OpenListError("Test error", 404)
        assert error.code == 404
        assert error.message == "Test error"
        assert str(error) == "[404] Test error"

    def test_error_default_code(self) -> None:
        """Test error with default status code."""
        error = OpenListError("Test error")
        assert error.code == 500


class TestOpenListClient:
    """Test cases for OpenListClient."""

    @pytest.fixture
    def mock_config(self) -> mock.MagicMock:
        """Create a mock config."""
        config = mock.MagicMock()
        config.base_url = "https://example.com"
        config.api_base = "https://example.com/api"
        config.username = "testuser"
        config.password = "testpass"
        config.is_authenticated = True
        return config

    @pytest.mark.asyncio
    async def test_parse_response_success(self, mock_config: mock.MagicMock) -> None:
        """Test parsing successful response."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            response = Response(200, json={"code": 200, "data": {"test": "value"}})
            result = client._parse_response(response)
            assert result == {"code": 200, "data": {"test": "value"}}

    @pytest.mark.asyncio
    async def test_parse_response_http_error(self, mock_config: mock.MagicMock) -> None:
        """Test parsing HTTP error response."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            response = Response(404, text="Not found")
            with pytest.raises(OpenListError, match="failed with HTTP 404"):
                client._parse_response(response)

    @pytest.mark.asyncio
    async def test_parse_response_non_json(self, mock_config: mock.MagicMock) -> None:
        """Test parsing non-JSON response."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            response = Response(200, text="not json")
            with pytest.raises(OpenListError, match="non-JSON response"):
                client._parse_response(response)

    @pytest.mark.asyncio
    async def test_parse_response_unexpected_type(self, mock_config: mock.MagicMock) -> None:
        """Test parsing response with unexpected type."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            response = Response(200, json=["list", "not", "dict"])
            with pytest.raises(OpenListError, match="unexpected response type"):
                client._parse_response(response)

    @pytest.mark.asyncio
    async def test_login_success(self, mock_config: mock.MagicMock) -> None:
        """Test successful login."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()

            mock_response = Response(
                200, json={"code": 200, "data": {"token": "test_token_123", "user": "testuser"}}
            )

            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.AsyncMock()
                mock_client.post = mock.AsyncMock(return_value=mock_response)
                mock_get_client.return_value = mock_client

                result = await client.login()

                assert client._token == "test_token_123"
                assert result == {"token": "test_token_123", "user": "testuser"}

    @pytest.mark.asyncio
    async def test_login_no_credentials(self, mock_config: mock.MagicMock) -> None:
        """Test login without credentials."""
        mock_config.is_authenticated = False
        mock_config.username = ""
        mock_config.password = ""

        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            with pytest.raises(
                OpenListError, match="OPENLIST_USERNAME and OPENLIST_PASSWORD are required"
            ):
                await client.login()

    @pytest.mark.asyncio
    async def test_login_wrong_credentials(self, mock_config: mock.MagicMock) -> None:
        """Test login with wrong credentials."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()

            mock_response = Response(200, json={"code": 401, "message": "password is incorrect"})

            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.AsyncMock()
                mock_client.post = mock.AsyncMock(return_value=mock_response)
                mock_get_client.return_value = mock_client

                with pytest.raises(OpenListError, match="password is incorrect"):
                    await client.login()

    @pytest.mark.asyncio
    async def test_ensure_authenticated_already_has_token(
        self, mock_config: mock.MagicMock
    ) -> None:
        """Test ensure_authenticated when token already exists."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            client._token = "existing_token"

            # Should not call login
            with mock.patch.object(client, "login") as mock_login:
                await client.ensure_authenticated()
                mock_login.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_success(self, mock_config: mock.MagicMock) -> None:
        """Test successful API request."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()
            client._token = "test_token"

            mock_response = Response(200, json={"code": 200, "data": {"files": []}})

            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.AsyncMock()
                mock_client.request = mock.AsyncMock(return_value=mock_response)
                mock_get_client.return_value = mock_client

                result = await client.request("GET", "fs/list")
                assert result == {"files": []}

    @pytest.mark.asyncio
    async def test_request_no_auth(self, mock_config: mock.MagicMock) -> None:
        """Test API request without authentication."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            client = OpenListClient()

            mock_response = Response(200, json={"code": 200, "data": {"settings": {}}})

            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.AsyncMock()
                mock_client.request = mock.AsyncMock(return_value=mock_response)
                mock_get_client.return_value = mock_client

                result = await client.request("GET", "public/settings", require_auth=False)
                assert result == {"settings": {}}

    @pytest.mark.asyncio
    async def test_get_client_singleton(self, mock_config: mock.MagicMock) -> None:
        """Test that get_client returns a singleton."""
        with mock.patch("openlist_mcp.client.get_config", return_value=mock_config):
            # Reset singleton
            import openlist_mcp.client as client_module

            client_module._client = None

            client1 = await get_client()
            client2 = await get_client()
            assert client1 is client2
