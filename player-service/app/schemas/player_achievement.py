import uuid
from datetime import datetime

from pydantic import BaseModel


class PlayerAchievementCreate(BaseModel):
    player_id: uuid.UUID
    achievement_id: int
    progress: int = 0
    unlock_at: datetime | None = None


class PlayerAchievementUpdate(BaseModel):
    progress: int | None = None
    unlock_at: datetime | None = None


class PlayerAchievementResponse(BaseModel):
    player_id: uuid.UUID
    achievement_id: int
    unlock_at: datetime | None
    progress: int

    model_config = {"from_attributes": True}
