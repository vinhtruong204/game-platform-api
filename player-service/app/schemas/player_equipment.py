import uuid

from pydantic import BaseModel

from app.models.player_equipment import SlotType


class PlayerEquipmentCreate(BaseModel):
    player_id: uuid.UUID
    slot_type: SlotType
    weapon_id: int


class PlayerEquipmentUpdate(BaseModel):
    weapon_id: int


class PlayerEquipmentResponse(BaseModel):
    player_id: uuid.UUID
    slot_type: SlotType
    weapon_id: int

    model_config = {"from_attributes": True}
