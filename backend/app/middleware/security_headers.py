from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.datastructures import MutableHeaders
from starlette.types import Message, Receive, Scope, Send

ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class SecurityHeadersMiddleware:
    """Apply browser-safe headers without changing API response bodies."""

    def __init__(self, app: ASGIApp, *, hsts_enabled: bool) -> None:
        self.app = app
        self.hsts_enabled = hsts_enabled

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault("x-content-type-options", "nosniff")
                headers.setdefault("x-frame-options", "DENY")
                headers.setdefault("referrer-policy", "no-referrer")
                headers.setdefault(
                    "permissions-policy",
                    "camera=(), microphone=(), geolocation=()",
                )
                headers.setdefault("cross-origin-opener-policy", "same-origin")
                if self.hsts_enabled:
                    headers.setdefault(
                        "strict-transport-security",
                        "max-age=31536000; includeSubDomains",
                    )
            await send(message)

        await self.app(scope, receive, send_with_headers)
