import uuid
from datetime import datetime

from pydantic import BaseModel


class PlayerProfileCreate(BaseModel):
    name: str
    slogan: str | None = None
    current_level_id: int = 1
    current_exp: int = 0


class PlayerProfileUpdate(BaseModel):
    name: str | None = None
    slogan: str | None = None
    current_level_id: int | None = None
    current_exp: int | None = None


class PlayerProfileResponse(BaseModel):
    player_id: uuid.UUID
    current_level_id: int
    name: str
    slogan: str | None
    current_exp: int
    is_new_player: bool
    create_at: datetime
    last_login_at: datetime

    model_config = {"from_attributes": True}
