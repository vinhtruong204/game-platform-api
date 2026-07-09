import uuid
from datetime import datetime

from pydantic import BaseModel


class PlayerRankCreate(BaseModel):
    player_id: uuid.UUID
    season_id: int
    rank_id: int
    current_point: int = 0


class PlayerRankUpdate(BaseModel):
    rank_id: int | None = None
    current_point: int | None = None


class PlayerRankResponse(BaseModel):
    player_id: uuid.UUID
    season_id: int
    rank_id: int
    current_point: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
