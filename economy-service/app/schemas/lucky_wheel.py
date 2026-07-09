from pydantic import BaseModel

from app.models.shop import ItemType, CurrencyType


class LuckyWheelItemCreate(BaseModel):
    wheel_type: CurrencyType
    slot_index: int
    item_id: int | None = None
    item_type: ItemType | None = None
    currency_reward: int | None = None
    shop_price: int = 0
    weight: int = 100
    display_name: str
    image: str


class LuckyWheelItemUpdate(BaseModel):
    wheel_type: CurrencyType | None = None
    slot_index: int | None = None
    item_id: int | None = None
    item_type: ItemType | None = None
    currency_reward: int | None = None
    shop_price: int | None = None
    weight: int | None = None
    display_name: str | None = None
    image: str | None = None


class LuckyWheelItemResponse(BaseModel):
    id: int
    wheel_type: CurrencyType
    slot_index: int
    item_id: int | None = None
    item_type: ItemType | None = None
    currency_reward: int | None = None
    shop_price: int
    weight: int
    display_name: str
    image: str

    model_config = {"from_attributes": True}
