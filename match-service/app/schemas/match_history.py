from datetime import datetime

from pydantic import BaseModel

from app.models.match_history import MatchStatus


class MatchHistoryCreate(BaseModel):
    map_id: int
    mode_id: int
    start_time: datetime
    end_time: datetime | None = None
    status: MatchStatus
    season_id: int | None = None


class MatchHistoryUpdate(BaseModel):
    map_id: int | None = None
    mode_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: MatchStatus | None = None
    season_id: int | None = None


class MatchHistoryResponse(BaseModel):
    match_id: int
    map_id: int
    mode_id: int
    start_time: datetime
    end_time: datetime | None
    status: MatchStatus
    season_id: int | None

    model_config = {"from_attributes": True}
