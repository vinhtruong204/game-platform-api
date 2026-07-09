import enum
import uuid

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class MatchResult(str, enum.Enum):
    win = "win"
    lose = "lose"


class MatchPlayer(Base):
    __tablename__ = "match_player"

    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("match_history.match_id"), primary_key=True)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kill: Mapped[int] = mapped_column(Integer, default=0)
    dead: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[MatchResult] = mapped_column(Enum(MatchResult, name="matchresult"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    exp_earned: Mapped[int] = mapped_column(Integer, default=0)
    reward_gold: Mapped[int] = mapped_column(Integer, default=0)

    match: Mapped["MatchHistory"] = relationship(back_populates="players")


from app.models.match_history import MatchHistory  # noqa: E402
