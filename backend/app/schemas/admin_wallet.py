from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AdminWalletCreditRequest(BaseModel):
    amount_coins: int = Field(ge=1, le=100_000)
    reason: str = Field(min_length=4, max_length=500)
    request_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9._:-]+$")

    @field_validator("reason", "request_id")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()


class AdminWalletCreditResponse(BaseModel):
    user_id: UUID
    wallet_entry_id: UUID
    transaction_id: str
    amount_coins: int = Field(gt=0)
    amount_points: int = Field(gt=0)
    balance_points: int = Field(ge=0)
    balance_coins: str
    idempotent: bool
