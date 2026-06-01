"""Configuration management for OpenList MCP Server."""

import logging
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class OpenListConfig:
    """Manages OpenList server configuration from environment variables."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("OPENLIST_URL", "").rstrip("/")
        self.username = os.environ.get("OPENLIST_USERNAME", "")
        self.password = os.environ.get("OPENLIST_PASSWORD", "")
        self.totp_secret = os.environ.get("OPENLIST_TOTP_SECRET", "")
        self.read_only = _env_flag("OPENLIST_READONLY")
        self.allowed_paths = _parse_allowed_paths(os.environ.get("OPENLIST_ALLOWED_PATHS", ""))
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
            if not _env_flag("OPENLIST_ALLOW_HTTP"):
                raise ValueError(
                    "OPENLIST_URL uses unencrypted HTTP, which is rejected by default. "
                    "If you understand the risks (credentials sent in plain text), "
                    "set OPENLIST_ALLOW_HTTP=true to allow HTTP connections."
                )
            logger.warning(
                "Using unencrypted HTTP transport. Credentials and token may be transmitted "
                "in plain text. Use HTTPS in production."
            )

    @property
    def api_base(self) -> str:
        """Base URL for API requests."""
        return f"{self.base_url}/api"

    @property
    def is_authenticated(self) -> bool:
        """Whether credentials are configured."""
        return bool(self.username and self.password)

    @property
    def has_totp_secret(self) -> bool:
        """Whether a TOTP secret is configured for automatic 2FA."""
        return bool(self.totp_secret)


def _env_flag(name: str) -> bool:
    """Parse common truthy environment variable values."""
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_allowed_paths(raw_value: str) -> list[str]:
    """Parse comma-separated OpenList path prefixes."""
    paths = []
    for item in raw_value.split(","):
        path = item.strip().replace("\\", "/").rstrip("/")
        if not path:
            continue
        if not path.startswith("/"):
            path = f"/{path}"
        paths.append(path or "/")
    return paths


# Global config instance
_config: OpenListConfig | None = None


def get_config() -> OpenListConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = OpenListConfig()
    return _config
