import enum
import uuid
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class QueueStatus(str, enum.Enum):
    waiting = "waiting"
    matched = "matched"


class MatchmakingQueue(Base):
    __tablename__ = "matchmaking_queue"

    queue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    rank_point: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    game_mode: Mapped[str] = mapped_column(String, nullable=False, server_default="rank")
    map_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("map.map_id"), nullable=True)
    mode_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("mode.mode_id"), nullable=True)
    players_per_team: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    status: Mapped[QueueStatus] = mapped_column(
        Enum(QueueStatus, name="queuestatus"), nullable=False, server_default="waiting"
    )
    matched_match_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("match_history.match_id"), nullable=True
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    matched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    match: Mapped["MatchHistory"] = relationship()


from app.models.match_history import MatchHistory  # noqa: E402
