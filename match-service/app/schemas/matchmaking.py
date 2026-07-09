import uuid
from datetime import datetime

from pydantic import BaseModel


class MatchmakingJoinRequest(BaseModel):
    rank_point: int = 0
    game_mode: str = "rank"
    map_id: int | None = None
    mode_id: int | None = None
    players_per_team: int = 1


class MatchmakingPlayerInfo(BaseModel):
    player_id: uuid.UUID
    team_id: int


class MatchmakingQueuedResponse(BaseModel):
    status: str = "queued"
    queue_id: int
    player_id: uuid.UUID
    position: int
    joined_at: datetime


class MatchmakingMatchFoundResponse(BaseModel):
    status: str = "match_found"
    match_id: int
    mode_id: int
    mode_name: str
    mode_code: str | None = None
    map_id: int
    map_name: str
    players_per_team: int
    players: list[MatchmakingPlayerInfo]


class MatchmakingWaitingResponse(BaseModel):
    status: str = "waiting"
    queue_id: int
    position: int
    wait_seconds: float
    joined_at: datetime


class MatchmakingMatchedResponse(BaseModel):
    status: str = "matched"
    match_id: int
    mode_id: int
    mode_name: str
    mode_code: str | None = None
    map_id: int
    map_name: str
    players_per_team: int
    players: list[MatchmakingPlayerInfo]


class MatchmakingNoneResponse(BaseModel):
    status: str = "none"


class MatchmakingLeftResponse(BaseModel):
    status: str = "left"
    player_id: uuid.UUID
