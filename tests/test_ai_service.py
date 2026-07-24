import asyncio

from sahmi_kasban.ai import AIChatClient, AIClientConfig, SahmiAIService


class FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response

    async def chat(self, messages, **kwargs):  # noqa: ANN001, ANN003
        return self.response


def test_open_webui_url_normalization() -> None:
    assert AIChatClient._normalize_open_webui_base("http://localhost:8080") == (
        "http://localhost:8080/api/v1"
    )
    assert AIChatClient._normalize_open_webui_base("http://localhost:8080/api/v1") == (
        "http://localhost:8080/api/v1"
    )


def test_client_config_parses_multiple_keys(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEYS", " first-key, second-key ")
    config = AIClientConfig.from_env()
    assert config.groq_api_keys == ("first-key", "second-key")


def test_moderation_parses_fenced_json() -> None:
    service = SahmiAIService(
        FakeClient(
            """```json
            {"approved": true, "category": "clean", "reason": "ok", "flags": []}
            ```"""
        )
    )
    result = asyncio.run(service.moderate_discussion("أتوقع صعود سهم معين"))
    assert result["approved"] is True
    assert result["flags"] == []


def test_verification_enforces_reward_table() -> None:
    service = SahmiAIService(
        FakeClient(
            '{"level":"strong","reward_coins":99,"score":0.8,"reason":"matched"}'
        )
    )
    result = asyncio.run(
        service.verify_prediction(
            prediction={"ticker": "JUFO", "direction": "up"},
            market_outcome={"change_percent": 4.0},
        )
    )
    assert result["level"] == "strong"
    assert result["reward_coins"] == 1.0
