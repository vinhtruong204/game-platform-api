import uuid

from pydantic import BaseModel


class PlayerSelectedCharacterCreate(BaseModel):
    player_id: uuid.UUID
    character_id: int


class PlayerSelectedCharacterUpdate(BaseModel):
    character_id: int


class PlayerSelectedCharacterResponse(BaseModel):
    player_id: uuid.UUID
    character_id: int

    model_config = {"from_attributes": True}
