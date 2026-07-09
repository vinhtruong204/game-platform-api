import uuid
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PlayerAchievement(Base):
    __tablename__ = "player_achievement"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unlock_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)

    player: Mapped["PlayerProfile"] = relationship(back_populates="achievements")


from app.models.player_profile import PlayerProfile  # noqa: E402
