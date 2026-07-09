import enum

from pydantic import BaseModel


class LeaderboardMode(str, enum.Enum):
    ranking = "ranking"
    normal = "normal"
    collector = "collector"


class LeaderboardEntry(BaseModel):
    position: int
    player_name: str
    # Ranking & Normal
    win_rate: float | None = None
    kda: float | None = None
    # Ranking only
    rank_name: str | None = None
    # Normal only
    total_game: int | None = None
    # Collector only
    weapon_count: int | None = None
    item_count: int | None = None
    character_count: int | None = None
    total_items: int | None = None


class LeaderboardResponse(BaseModel):
    mode: LeaderboardMode
    entries: list[LeaderboardEntry]
