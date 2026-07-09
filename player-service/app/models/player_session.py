import uuid
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PlayerSession(Base):
    __tablename__ = "player_session"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), nullable=False)
    auth_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_auth.auth_id", ondelete="CASCADE"), nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    player: Mapped["PlayerProfile"] = relationship()
    auth: Mapped["PlayerAuth"] = relationship(back_populates="sessions")


from app.models.player_profile import PlayerProfile  # noqa: E402
from app.models.player_auth import PlayerAuth  # noqa: E402
