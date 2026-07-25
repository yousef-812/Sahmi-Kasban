from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import service_account

from app.core.config import Settings, get_settings


class MonetizationVerificationError(RuntimeError):
    """Raised when Google or AdMob verification cannot be trusted."""


class MonetizationConfigurationError(MonetizationVerificationError):
    """Raised when a live verifier is missing required credentials."""


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PurchaseTokenCipher:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        configured = self._settings.billing_token_encryption_key.strip()
        if configured:
            key = configured.encode("ascii")
        else:
            digest = hashlib.sha256(
                f"billing:{self._settings.secret_key}".encode("utf-8")
            ).digest()
            key = base64.urlsafe_b64encode(digest)
        try:
            self._fernet = Fernet(key)
        except (TypeError, ValueError) as exc:
            raise MonetizationConfigurationError(
                "BILLING_TOKEN_ENCRYPTION_KEY must be a valid Fernet key"
            ) from exc

    def encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode("utf-8")).decode("ascii")

    def decrypt(self, encrypted_token: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_token.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise MonetizationVerificationError("Stored purchase token cannot be decrypted") from exc


@dataclass(frozen=True, slots=True)
class VerifiedPurchase:
    product_id: str
    product_type: str
    state: str
    acknowledgement_state: str
    quantity: int
    order_id: str | None
    expires_at: datetime | None
    linked_purchase_token: str | None
    raw_payload: dict[str, Any]

    @property
    def purchased(self) -> bool:
        return self.state == "purchased"


class GooglePlayVerifier:
    _scope = "https://www.googleapis.com/auth/androidpublisher"
    _api_root = "https://androidpublisher.googleapis.com/androidpublisher/v3"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._credentials: service_account.Credentials | None = None

    async def verify(
        self,
        *,
        product_id: str,
        product_type: str,
        purchase_token: str,
    ) -> VerifiedPurchase:
        mode = self.settings.google_play_verification_mode
        if mode == "disabled":
            raise MonetizationConfigurationError("Google Play verification is disabled")
        if mode == "stub":
            return self._verify_stub(
                product_id=product_id,
                product_type=product_type,
                purchase_token=purchase_token,
            )
        if product_type == "subscription":
            return await self._verify_subscription(product_id, purchase_token)
        if product_type == "coins":
            return await self._verify_product(product_id, purchase_token)
        raise MonetizationVerificationError("Unsupported Google Play product type")

    async def acknowledge(
        self,
        *,
        verified: VerifiedPurchase,
        purchase_token: str,
    ) -> None:
        if self.settings.google_play_verification_mode == "stub":
            return
        access_token = await self._access_token()
        package_name = self.settings.google_play_package_name
        headers = {"Authorization": f"Bearer {access_token}"}
        if verified.product_type == "coins":
            url = (
                f"{self._api_root}/applications/{package_name}/purchases/products/"
                f"{verified.product_id}/tokens/{purchase_token}:consume"
            )
        else:
            url = (
                f"{self._api_root}/applications/{package_name}/purchases/subscriptions/"
                f"{verified.product_id}/tokens/{purchase_token}:acknowledge"
            )
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=headers, json={})
        if response.status_code not in {200, 204, 409}:
            raise MonetizationVerificationError(
                f"Google Play acknowledgement failed with status {response.status_code}"
            )

    def _verify_stub(
        self,
        *,
        product_id: str,
        product_type: str,
        purchase_token: str,
    ) -> VerifiedPurchase:
        prefix = "stub-purchased:"
        if not purchase_token.startswith(prefix):
            raise MonetizationVerificationError("Stub purchase token is not marked purchased")
        token_parts = purchase_token.split(":", maxsplit=3)
        order_id = token_parts[2] if len(token_parts) >= 3 else None
        expires_at = None
        if product_type == "subscription":
            expires_at = datetime.now(UTC) + timedelta(days=30)
        return VerifiedPurchase(
            product_id=product_id,
            product_type=product_type,
            state="purchased",
            acknowledgement_state="pending",
            quantity=1,
            order_id=order_id,
            expires_at=expires_at,
            linked_purchase_token=None,
            raw_payload={"verification_mode": "stub"},
        )

    async def _verify_product(
        self,
        product_id: str,
        purchase_token: str,
    ) -> VerifiedPurchase:
        package_name = self.settings.google_play_package_name
        payload = await self._get_json(
            f"{self._api_root}/applications/{package_name}/purchases/products/"
            f"{product_id}/tokens/{purchase_token}"
        )
        purchase_state = int(payload.get("purchaseState", 1))
        state = "purchased" if purchase_state == 0 else "pending" if purchase_state == 2 else "cancelled"
        acknowledgement_state = (
            "acknowledged" if int(payload.get("acknowledgementState", 0)) == 1 else "pending"
        )
        return VerifiedPurchase(
            product_id=product_id,
            product_type="coins",
            state=state,
            acknowledgement_state=acknowledgement_state,
            quantity=max(1, int(payload.get("quantity", 1))),
            order_id=payload.get("orderId"),
            expires_at=None,
            linked_purchase_token=None,
            raw_payload=payload,
        )

    async def _verify_subscription(
        self,
        product_id: str,
        purchase_token: str,
    ) -> VerifiedPurchase:
        package_name = self.settings.google_play_package_name
        payload = await self._get_json(
            f"{self._api_root}/applications/{package_name}/purchases/subscriptionsv2/"
            f"tokens/{purchase_token}"
        )
        state_name = str(payload.get("subscriptionState", ""))
        state = (
            "purchased"
            if state_name
            in {
                "SUBSCRIPTION_STATE_ACTIVE",
                "SUBSCRIPTION_STATE_IN_GRACE_PERIOD",
                "SUBSCRIPTION_STATE_CANCELED",
            }
            else "pending"
            if state_name == "SUBSCRIPTION_STATE_PENDING"
            else "expired"
        )
        acknowledgement_state = (
            "acknowledged"
            if payload.get("acknowledgementState") == "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED"
            else "pending"
        )
        line_items = payload.get("lineItems") or []
        matching_item = next(
            (item for item in line_items if item.get("productId") == product_id),
            None,
        )
        if matching_item is None:
            raise MonetizationVerificationError(
                "Verified subscription does not contain the requested product"
            )
        expires_at = _parse_google_timestamp(matching_item.get("expiryTime"))
        latest_order_id = matching_item.get("latestSuccessfulOrderId")
        return VerifiedPurchase(
            product_id=product_id,
            product_type="subscription",
            state=state,
            acknowledgement_state=acknowledgement_state,
            quantity=1,
            order_id=latest_order_id,
            expires_at=expires_at,
            linked_purchase_token=payload.get("linkedPurchaseToken"),
            raw_payload=payload,
        )

    async def _get_json(self, url: str) -> dict[str, Any]:
        access_token = await self._access_token()
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code != 200:
            raise MonetizationVerificationError(
                f"Google Play verification failed with status {response.status_code}"
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise MonetizationVerificationError("Google Play returned an invalid payload")
        return payload

    async def _access_token(self) -> str:
        credentials = self._credentials
        if credentials is None:
            raw = self.settings.google_play_service_account_json.strip()
            if not raw:
                raise MonetizationConfigurationError(
                    "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON is not configured"
                )
            try:
                info = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise MonetizationConfigurationError(
                    "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON is not valid JSON"
                ) from exc
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=[self._scope],
            )
            self._credentials = credentials
        if not credentials.valid or not credentials.token:
            await asyncio.to_thread(credentials.refresh, GoogleAuthRequest())
        if not credentials.token:
            raise MonetizationVerificationError("Google OAuth access token is unavailable")
        return credentials.token


@dataclass(slots=True)
class _AdMobKeyCache:
    keys: dict[int, ec.EllipticCurvePublicKey]
    expires_at: datetime


_admob_key_cache: _AdMobKeyCache | None = None
_admob_key_lock = asyncio.Lock()


class AdMobSsvVerifier:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def verify(self, raw_query: str) -> None:
        mode = self.settings.admob_ssv_verification_mode
        if mode == "disabled":
            raise MonetizationConfigurationError("AdMob SSV verification is disabled")
        if mode == "stub":
            if "signature=stub-valid&key_id=0" not in raw_query:
                raise MonetizationVerificationError("Invalid stub AdMob signature")
            return

        signature_marker = "&signature="
        key_marker = "&key_id="
        signature_index = raw_query.find(signature_marker)
        key_index = raw_query.find(key_marker, signature_index + 1)
        if signature_index < 0 or key_index < 0:
            raise MonetizationVerificationError(
                "AdMob callback must end with signature and key_id"
            )
        if key_index < signature_index:
            raise MonetizationVerificationError("AdMob callback parameter order is invalid")

        content = raw_query[:signature_index].encode("utf-8")
        encoded_signature = raw_query[
            signature_index + len(signature_marker) : key_index
        ]
        key_id_text = raw_query[key_index + len(key_marker) :]
        if "&" in key_id_text:
            raise MonetizationVerificationError("AdMob key_id must be the final parameter")
        try:
            key_id = int(key_id_text)
            signature = _urlsafe_b64decode(encoded_signature)
        except (ValueError, TypeError) as exc:
            raise MonetizationVerificationError("Invalid AdMob signature metadata") from exc

        keys = await self._public_keys()
        public_key = keys.get(key_id)
        if public_key is None:
            raise MonetizationVerificationError("Unknown AdMob signing key")
        try:
            public_key.verify(signature, content, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature as exc:
            raise MonetizationVerificationError("Invalid AdMob SSV signature") from exc

    async def _public_keys(self) -> dict[int, ec.EllipticCurvePublicKey]:
        global _admob_key_cache
        now = datetime.now(UTC)
        cached = _admob_key_cache
        if cached is not None and cached.expires_at > now:
            return cached.keys
        async with _admob_key_lock:
            cached = _admob_key_cache
            if cached is not None and cached.expires_at > now:
                return cached.keys
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.settings.admob_ssv_keys_url)
            if response.status_code != 200:
                raise MonetizationVerificationError(
                    f"AdMob key server returned status {response.status_code}"
                )
            payload = response.json()
            parsed: dict[int, ec.EllipticCurvePublicKey] = {}
            for item in payload.get("keys", []):
                key_id = int(item["keyId"])
                der = base64.b64decode(item["base64"])
                key = serialization.load_der_public_key(der)
                if not isinstance(key, ec.EllipticCurvePublicKey):
                    raise MonetizationVerificationError("AdMob signing key is not EC")
                parsed[key_id] = key
            if not parsed:
                raise MonetizationVerificationError("AdMob key server returned no keys")
            _admob_key_cache = _AdMobKeyCache(
                keys=parsed,
                expires_at=now + timedelta(hours=24),
            )
            return parsed


def _parse_google_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MonetizationVerificationError("Google returned an invalid expiry timestamp") from exc
    return parsed.astimezone(UTC)


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
