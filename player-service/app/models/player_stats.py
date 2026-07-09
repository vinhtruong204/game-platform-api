import enum
import uuid

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class GameMode(str, enum.Enum):
    normal = "normal"
    rank = "rank"


class PlayerStats(Base):
    __tablename__ = "player_stats"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    mode: Mapped[GameMode] = mapped_column(Enum(GameMode, name="gamemode"), primary_key=True)
    current_point: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_game: Mapped[int] = mapped_column(Integer, default=0)
    number_games_win: Mapped[int] = mapped_column(Integer, default=0)
    kill: Mapped[int] = mapped_column(Integer, default=0)
    dead: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)

    player: Mapped["PlayerProfile"] = relationship(back_populates="stats")


from app.models.player_profile import PlayerProfile  # noqa: E402
