"""Tests for configuration management."""

import os
from unittest import mock

import pytest

from openlist_mcp.config import OpenListConfig, get_config


class TestOpenListConfig:
    """Test cases for OpenListConfig."""

    def test_valid_config(self) -> None:
        """Test configuration with valid environment variables."""
        with mock.patch.dict(
            os.environ,
            {
                "OPENLIST_URL": "https://example.com",
                "OPENLIST_USERNAME": "testuser",
                "OPENLIST_PASSWORD": "testpass",
            },
        ):
            config = OpenListConfig()
            assert config.base_url == "https://example.com"
            assert config.username == "testuser"
            assert config.password == "testpass"
            assert config.api_base == "https://example.com/api"
            assert config.is_authenticated is True

    def test_url_without_trailing_slash(self) -> None:
        """Test that trailing slash is removed from URL."""
        with mock.patch.dict(
            os.environ,
            {
                "OPENLIST_URL": "https://example.com/",
            },
        ):
            config = OpenListConfig()
            assert config.base_url == "https://example.com"

    def test_missing_url_raises_error(self) -> None:
        """Test that missing URL raises ValueError."""
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="OPENLIST_URL is required"),
        ):
            OpenListConfig()

    def test_invalid_url_scheme(self) -> None:
        """Test that invalid URL scheme raises ValueError."""
        with (
            mock.patch.dict(
                os.environ,
                {
                    "OPENLIST_URL": "ftp://example.com",
                },
                clear=True,
            ),
            pytest.raises(ValueError, match="must start with http:// or https://"),
        ):
            OpenListConfig()

    def test_partial_auth_config(self) -> None:
        """Test configuration with only username or only password."""
        with mock.patch.dict(
            os.environ,
            {
                "OPENLIST_URL": "https://example.com",
                "OPENLIST_USERNAME": "testuser",
            },
            clear=True,
        ):
            config = OpenListConfig()
            assert config.is_authenticated is False

        with mock.patch.dict(
            os.environ,
            {
                "OPENLIST_URL": "https://example.com",
                "OPENLIST_PASSWORD": "testpass",
            },
            clear=True,
        ):
            config = OpenListConfig()
            assert config.is_authenticated is False

    def test_get_config_singleton(self) -> None:
        """Test that get_config returns a singleton instance."""
        with mock.patch.dict(
            os.environ,
            {
                "OPENLIST_URL": "https://example.com",
            },
        ):
            # Reset the singleton for testing
            import openlist_mcp.config as config_module

            config_module._config = None

            config1 = get_config()
            config2 = get_config()
            assert config1 is config2
