from typing import Literal

from pydantic import BaseModel, Field

from app.models.player_currency import CurrencyType
from app.models.player_inventory import ItemType


class PurchaseRequest(BaseModel):
    item_id: int
    item_type: ItemType
    currency_type: CurrencyType
    price: int = Field(..., gt=0)


class PurchaseResponse(BaseModel):
    item_id: int
    item_type: ItemType
    quantity: int
    currency_type: CurrencyType
    amount_spent: int
    currency_remaining: int


class GooglePurchaseVerifyRequest(BaseModel):
    purchase_token: str = Field(..., min_length=1, max_length=512)
    sku: str = Field(..., min_length=1, max_length=128)
    platform: Literal["google_play"] = "google_play"


class GooglePurchaseVerifyResponse(BaseModel):
    credited: int
    currency_type: CurrencyType
    new_balance: int
    idempotent: bool
