from __future__ import annotations

import asyncio
import os
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx


class AIProviderError(RuntimeError):
    """Raised when all configured AI providers fail."""


@dataclass(frozen=True, slots=True)
class AIClientConfig:
    """Configuration for Open-WebUI and Groq-compatible chat APIs."""

    open_webui_url: str = ""
    open_webui_api_key: str = ""
    groq_api_keys: tuple[str, ...] = ()
    default_model: str = "llama-3.3-70b-versatile"
    timeout_seconds: float = 45.0
    max_tokens: int = 1800
    temperature: float = 0.2

    @classmethod
    def from_env(cls) -> "AIClientConfig":
        raw_keys = os.getenv("GROQ_API_KEYS", "")
        keys = tuple(key.strip() for key in raw_keys.split(",") if key.strip())
        return cls(
            open_webui_url=os.getenv("OPEN_WEBUI_URL", "").strip(),
            open_webui_api_key=os.getenv("OPEN_WEBUI_API_KEY", "").strip(),
            groq_api_keys=keys,
            default_model=os.getenv("AI_MODEL", "llama-3.3-70b-versatile").strip(),
            timeout_seconds=float(os.getenv("AI_TIMEOUT_SECONDS", "45")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1800")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.2")),
        )


class AIChatClient:
    """Async chat client with Open-WebUI primary and Groq key-rotation fallback."""

    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, config: AIClientConfig | None = None) -> None:
        self.config = config or AIClientConfig.from_env()
        self._key_index = 0
        self._key_lock = asyncio.Lock()

    @staticmethod
    def _normalize_open_webui_base(url: str) -> str:
        base = url.rstrip("/")
        if not base:
            return ""
        if base.endswith("/chat/completions"):
            return base.removesuffix("/chat/completions")
        if base.endswith(("/v1", "/api/v1", "/api")):
            return base
        return f"{base}/api/v1"

    @staticmethod
    def _headers(api_key: str) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    async def _ordered_groq_keys(self) -> tuple[str, ...]:
        async with self._key_lock:
            keys = self.config.groq_api_keys
            if not keys:
                return ()
            start = self._key_index % len(keys)
            ordered = keys[start:] + keys[:start]
            self._key_index = (start + 1) % len(keys)
            return ordered

    async def _post_completion(
        self,
        *,
        base_url: str,
        api_key: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.post(url, headers=self._headers(api_key), json=payload)
        if response.status_code >= 400:
            detail = response.text[:500]
            raise AIProviderError(f"AI provider returned {response.status_code}: {detail}")
        try:
            return response.json()
        except ValueError as exc:
            raise AIProviderError("AI provider returned invalid JSON") from exc

    async def chat(
        self,
        messages: Iterable[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.config.default_model,
            "messages": list(messages),
            "temperature": self.config.temperature if temperature is None else temperature,
            "max_tokens": self.config.max_tokens if max_tokens is None else max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        failures: list[str] = []
        open_webui_base = self._normalize_open_webui_base(self.config.open_webui_url)
        if open_webui_base:
            try:
                data = await self._post_completion(
                    base_url=open_webui_base,
                    api_key=self.config.open_webui_api_key,
                    payload=payload,
                )
                return self._extract_content(data)
            except (AIProviderError, httpx.HTTPError) as exc:
                failures.append(f"Open-WebUI: {exc}")

        for key in await self._ordered_groq_keys():
            try:
                data = await self._post_completion(
                    base_url=self.GROQ_BASE_URL,
                    api_key=key,
                    payload=payload,
                )
                return self._extract_content(data)
            except (AIProviderError, httpx.HTTPError) as exc:
                failures.append(f"Groq: {exc}")

        if not open_webui_base and not self.config.groq_api_keys:
            raise AIProviderError(
                "No AI provider configured. Set OPEN_WEBUI_URL or GROQ_API_KEYS."
            )
        raise AIProviderError("All AI providers failed. " + " | ".join(failures))

    async def list_models(self) -> list[str]:
        providers: list[tuple[str, str]] = []
        open_webui_base = self._normalize_open_webui_base(self.config.open_webui_url)
        if open_webui_base:
            providers.append((open_webui_base, self.config.open_webui_api_key))
        keys = await self._ordered_groq_keys()
        if keys:
            providers.append((self.GROQ_BASE_URL, keys[0]))

        for base_url, key in providers:
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.get(
                        f"{base_url.rstrip('/')}/models",
                        headers=self._headers(key),
                    )
                response.raise_for_status()
                data = response.json()
                models = [item["id"] for item in data.get("data", []) if item.get("id")]
                if models:
                    return models
            except (httpx.HTTPError, ValueError, KeyError):
                continue
        return [self.config.default_model]

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI response is missing message content") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI response content is empty")
        return content.strip()
