"""Configuration management for OpenList MCP Server."""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class OpenListConfig:
    """Manages OpenList server configuration from environment variables."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("OPENLIST_URL", "").rstrip("/")
        self.username = os.environ.get("OPENLIST_USERNAME", "")
        self.password = os.environ.get("OPENLIST_PASSWORD", "")
        self._validate()

    def _validate(self) -> None:
        if not self.base_url:
            raise ValueError(
                "OPENLIST_URL is required. "
                "Please set it via environment variable, e.g.: "
                "export OPENLIST_URL=https://your-openlist-instance.com"
            )
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(
                f"OPENLIST_URL must start with http:// or https://, got: {self.base_url}"
            )
        if self.base_url.startswith("http://"):
            import warnings
            warnings.warn(
                "Using unencrypted HTTP transport is insecure. "
                "Please consider using HTTPS for production environments.",
                UserWarning,
                stacklevel=2,
            )

    @property
    def api_base(self) -> str:
        """Base URL for API requests."""
        return f"{self.base_url}/api"

    @property
    def is_authenticated(self) -> bool:
        """Whether credentials are configured."""
        return bool(self.username and self.password)


# Global config instance
_config: OpenListConfig | None = None


def get_config() -> OpenListConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = OpenListConfig()
    return _config
