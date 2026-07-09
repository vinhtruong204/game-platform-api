from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.map import Map  # noqa: E402
from app.models.mode import Mode  # noqa: E402
from app.models.match_history import MatchHistory  # noqa: E402
from app.models.match_player import MatchPlayer  # noqa: E402
from app.models.matchmaking_queue import MatchmakingQueue  # noqa: E402

__all__ = [
    "Base",
    "Map",
    "Mode",
    "MatchHistory",
    "MatchPlayer",
    "MatchmakingQueue",
]
