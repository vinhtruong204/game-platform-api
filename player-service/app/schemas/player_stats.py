import uuid

from pydantic import BaseModel

from app.models.player_stats import GameMode


class PlayerStatsCreate(BaseModel):
    player_id: uuid.UUID
    mode: GameMode
    current_point: int | None = None
    total_game: int = 0
    number_games_win: int = 0
    kill: int = 0
    dead: int = 0
    assists: int = 0


class PlayerStatsUpdate(BaseModel):
    current_point: int | None = None
    total_game: int | None = None
    number_games_win: int | None = None
    kill: int | None = None
    dead: int | None = None
    assists: int | None = None


class PlayerStatsResponse(BaseModel):
    player_id: uuid.UUID
    mode: GameMode
    current_point: int | None
    total_game: int
    number_games_win: int
    kill: int
    dead: int
    assists: int

    model_config = {"from_attributes": True}
