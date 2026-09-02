from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.security_headers import SecurityHeadersMiddleware


def _client(*, hsts_enabled: bool) -> TestClient:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, hsts_enabled=hsts_enabled)

    @app.get("/probe")
    def probe() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_security_headers_are_added_to_http_responses() -> None:
    response = _client(hsts_enabled=False).get("/probe")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == ("camera=(), microphone=(), geolocation=()")
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert "strict-transport-security" not in response.headers


def test_hsts_is_enabled_only_for_production_configuration() -> None:
    response = _client(hsts_enabled=True).get("/probe")

    assert response.headers["strict-transport-security"] == ("max-age=31536000; includeSubDomains")
