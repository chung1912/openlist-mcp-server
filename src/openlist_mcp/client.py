"""OpenList API client with JWT authentication management."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterable
from typing import Any

import httpx

from .config import get_config

logger = logging.getLogger(__name__)


def _generate_totp(secret: str) -> str:
    """Generate a TOTP code from the given secret using pyotp."""
    import pyotp

    totp = pyotp.TOTP(secret)
    return totp.now()


class OpenListError(Exception):
    """Error from OpenList API."""

    def __init__(self, message: str, code: int = 500):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class OpenList2FAError(OpenListError):
    """Login requires a 2FA (TOTP) code."""

    def __init__(self, message: str = "2FA code is required"):
        super().__init__(message, code=402)


class OpenListClient:
    """Async HTTP client for OpenList REST API with automatic JWT token management."""

    def __init__(self) -> None:
        self._config = get_config()
        self._token: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()
        self._2fa_cached: bool = False

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._config.api_base,
                timeout=httpx.Timeout(120.0, connect=10.0, write=120.0),
                follow_redirects=True,
            )
        return self._client

    @property
    def _headers(self) -> dict[str, str]:
        """Build request headers with JWT token.

        OpenList uses token directly in Authorization header (not Bearer format).
        """
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = self._token
        return headers

    def _parse_response(self, resp: httpx.Response, action: str = "Request") -> dict[str, Any]:
        """Parse an OpenList JSON response and raise friendly errors."""
        text_preview = resp.text[:300].replace("\n", " ").strip()
        if resp.status_code < 200 or resp.status_code >= 300:
            raise OpenListError(
                f"{action} failed with HTTP {resp.status_code}: {text_preview}",
                code=resp.status_code,
            )
        try:
            data = resp.json()
        except ValueError as exc:
            if text_preview.lower().startswith("<!doctype html") or "<html" in text_preview.lower():
                raise OpenListError(
                    f"{action} returned HTML instead of JSON. "
                    "This endpoint may be unavailable in your OpenList version or deployment.",
                    code=resp.status_code,
                ) from exc
            raise OpenListError(
                f"{action} returned non-JSON response: {text_preview}",
                code=resp.status_code,
            ) from exc
        if not isinstance(data, dict):
            raise OpenListError(f"{action} returned unexpected response type", code=500)
        return data

    async def ensure_authenticated(self) -> None:
        """Ensure we have a valid JWT token. Login if needed."""
        if self._token:
            return
        if self._2fa_cached and not self._config.has_totp_secret:
            raise OpenList2FAError(
                "2FA is enabled on this OpenList account. "
                "Call the login tool with the otp_code parameter to authenticate."
            )
        async with self._lock:
            if self._token:
                return
            if self._2fa_cached and not self._config.has_totp_secret:
                raise OpenList2FAError(
                    "2FA is enabled on this OpenList account. "
                    "Call the login tool with the otp_code parameter to authenticate."
                )
            try:
                otp_code = (
                    _generate_totp(self._config.totp_secret)
                    if self._config.has_totp_secret
                    else None
                )
                await self.login(otp_code=otp_code)
            except OpenList2FAError:
                self._2fa_cached = True
                if self._config.has_totp_secret:
                    raise OpenListError(
                        "Auto-generated TOTP code was rejected. "
                        "Check your OPENLIST_TOTP_SECRET value.",
                        code=402,
                    ) from None
                raise OpenList2FAError(
                    "2FA is enabled on this OpenList account. "
                    "Call the login tool with the otp_code parameter to authenticate."
                ) from None

    async def login(self, otp_code: str | None = None) -> dict[str, Any]:
        """Login to OpenList and store JWT token.

        Args:
            otp_code: TOTP code for 2FA. Required if the user has enabled
                      two-factor authentication on their OpenList account.
        """
        if not self._config.is_authenticated:
            raise OpenListError(
                "OPENLIST_USERNAME and OPENLIST_PASSWORD are required for authentication.",
                code=401,
            )

        body: dict[str, str] = {
            "username": self._config.username,
            "password": self._config.password,
        }
        if otp_code:
            body["otp_code"] = otp_code

        client = await self._get_client()
        try:
            resp = await client.post("/auth/login", json=body)
        except httpx.HTTPError as exc:
            raise OpenListError(f"Login request failed: {exc}", code=503) from exc

        data = self._parse_response(resp, "Login")
        code: int = data.get("code", 500)
        if code != 200:
            # 2FA code required or invalid
            if code == 402:
                if otp_code:
                    raise OpenListError(
                        "Invalid 2FA code. Please re-run login with a valid TOTP code.",
                        code=402,
                    )
                raise OpenList2FAError()
            raise OpenListError(
                data.get("message", "Login failed"),
                code=code,
            )

        result_data = data.get("data", {})
        if not isinstance(result_data, dict):
            raise OpenListError("Login returned unexpected data format", code=500)
        token = result_data.get("token")
        if not token:
            raise OpenListError("Login succeeded but no token was returned", code=500)
        self._token = token
        self._2fa_cached = False
        logger.info("Login successful")
        return result_data

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        require_auth: bool = True,
    ) -> dict[str, Any]:
        """Make an API request to OpenList."""
        if require_auth:
            await self.ensure_authenticated()

        client = await self._get_client()
        try:
            resp = await client.request(
                method,
                f"/{path.lstrip('/')}",
                json=json,
                params=params,
                headers=self._headers,
            )
        except httpx.HTTPError as exc:
            raise OpenListError(f"Request failed: {exc}", code=503) from exc

        data = self._parse_response(resp, f"{method.upper()} {path}")
        if data.get("code") != 200:
            if data.get("code") == 401 and self._token and require_auth:
                self._token = None
                await self.ensure_authenticated()
                try:
                    resp = await client.request(
                        method,
                        f"/{path.lstrip('/')}",
                        json=json,
                        params=params,
                        headers=self._headers,
                    )
                except httpx.HTTPError as exc:
                    raise OpenListError(f"Request retry failed: {exc}", code=503) from exc
                data = self._parse_response(resp, f"{method.upper()} {path} retry")
                if data.get("code") != 200:
                    self._token = None
                    raise OpenListError(
                        data.get("message", "Request failed"),
                        code=data.get("code", 500),
                    )
            else:
                raise OpenListError(
                    data.get("message", "Request failed"), code=data.get("code", 500)
                )

        result = data.get("data", {})
        return result if isinstance(result, dict) else {"value": result}

    async def upload(
        self,
        path: str,
        file_content: bytes | AsyncIterable[bytes],
        file_name: str,
        as_task: bool = True,
    ) -> dict[str, Any]:
        """Upload a file to OpenList."""
        await self.ensure_authenticated()
        client = await self._get_client()

        url = "/fs/put"
        if as_task:
            url += "?as_task=true"

        target_path = f"{path.rstrip('/')}/{file_name}" if path != "/" else f"/{file_name}"
        try:
            resp = await client.put(
                url,
                content=file_content,
                headers={
                    "Authorization": self._token or "",
                    "File-Path": target_path,
                    "Content-Type": "application/octet-stream",
                },
            )
        except httpx.HTTPError as exc:
            raise OpenListError(f"Upload request failed: {exc}", code=503) from exc

        data = self._parse_response(resp, "Upload")
        if data.get("code") != 200:
            raise OpenListError(data.get("message", "Upload failed"), code=data.get("code", 500))

        result = data.get("data", {})
        return result if isinstance(result, dict) else {"value": result}

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


_client: OpenListClient | None = None


async def get_client() -> OpenListClient:
    """Get or create the global OpenList client instance."""
    global _client
    if _client is None:
        _client = OpenListClient()
    return _client
