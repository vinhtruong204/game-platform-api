import uuid

from pydantic import BaseModel

from app.models.match_player import MatchResult


class MatchPlayerCreate(BaseModel):
    match_id: int
    player_id: uuid.UUID
    team_id: int
    kill: int = 0
    dead: int = 0
    assists: int = 0
    result: MatchResult
    score: int = 0
    exp_earned: int = 0
    reward_gold: int = 0


class MatchPlayerUpdate(BaseModel):
    team_id: int | None = None
    kill: int | None = None
    dead: int | None = None
    assists: int | None = None
    result: MatchResult | None = None
    score: int | None = None
    exp_earned: int | None = None
    reward_gold: int | None = None


class MatchPlayerResponse(BaseModel):
    match_id: int
    player_id: uuid.UUID
    team_id: int
    kill: int
    dead: int
    assists: int
    result: MatchResult
    score: int
    exp_earned: int
    reward_gold: int

    model_config = {"from_attributes": True}


class WinningStreakResponse(BaseModel):
    player_id: uuid.UUID
    winning_streak: int
