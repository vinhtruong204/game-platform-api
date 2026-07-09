import enum
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class MatchStatus(str, enum.Enum):
    pending = "pending"
    finished = "finished"
    abandoned = "abandoned"


class MatchHistory(Base):
    __tablename__ = "match_history"

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    map_id: Mapped[int] = mapped_column(Integer, ForeignKey("map.map_id"), nullable=False)
    mode_id: Mapped[int] = mapped_column(Integer, ForeignKey("mode.mode_id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus, name="matchstatus"), nullable=False)
    season_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    map: Mapped["Map"] = relationship(back_populates="matches")
    mode: Mapped["Mode"] = relationship(back_populates="matches")
    players: Mapped[list["MatchPlayer"]] = relationship(back_populates="match")


from app.models.map import Map  # noqa: E402
from app.models.mode import Mode  # noqa: E402
from app.models.match_player import MatchPlayer  # noqa: E402
