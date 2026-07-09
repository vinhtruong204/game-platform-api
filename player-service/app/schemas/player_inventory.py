import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.player_inventory import ItemType


class PlayerInventoryCreate(BaseModel):
    player_id: uuid.UUID
    item_id: int
    item_type: ItemType
    quantity: int = 1


class PlayerInventoryUpdate(BaseModel):
    quantity: int | None = None


class PlayerInventoryResponse(BaseModel):
    player_id: uuid.UUID
    item_id: int
    item_type: ItemType
    quantity: int
    obtain_at: datetime

    model_config = {"from_attributes": True}
