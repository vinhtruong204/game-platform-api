from pydantic import BaseModel, Field

from app.models.player_currency import CurrencyType
from app.models.player_inventory import ItemType


class SpinRequest(BaseModel):
    wheel_type: CurrencyType
    spin_count: int = Field(1, ge=1, le=10)


class SpinResultItem(BaseModel):
    slot_index: int
    item_id: int | None = None
    item_type: ItemType | None = None
    currency_reward: int | None = None
    display_name: str
    image: str
    is_duplicate: bool = False
    compensation_amount: int = 0


class SpinResponse(BaseModel):
    results: list[SpinResultItem]
    currency_type: CurrencyType
    total_cost: int
    currency_remaining: int
