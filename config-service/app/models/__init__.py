from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.weapon import Weapon  # noqa: E402
from app.models.character import Character  # noqa: E402
from app.models.achievement import Achievement  # noqa: E402
from app.models.level_config import LevelConfig  # noqa: E402
from app.models.rank_config import RankConfig  # noqa: E402

__all__ = [
    "Base",
    "Weapon",
    "Character",
    "Achievement",
    "LevelConfig",
    "RankConfig",
]
