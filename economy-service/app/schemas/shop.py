from datetime import datetime

from pydantic import BaseModel

from app.models.shop import ItemType, CurrencyType


class ShopCreate(BaseModel):
    item_id: int
    item_type: ItemType
    price: int
    currency_type: CurrencyType
    discount: float = 0.0
    is_today: bool = False
    start_at: datetime
    end_at: datetime


class ShopUpdate(BaseModel):
    item_id: int | None = None
    item_type: ItemType | None = None
    price: int | None = None
    currency_type: CurrencyType | None = None
    discount: float | None = None
    is_today: bool | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class ShopResponse(BaseModel):
    shop_id: int
    item_id: int
    item_type: ItemType
    price: int
    currency_type: CurrencyType
    discount: float
    is_today: bool
    start_at: datetime
    end_at: datetime

    model_config = {"from_attributes": True}
