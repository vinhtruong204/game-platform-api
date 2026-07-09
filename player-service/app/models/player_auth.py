import uuid
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.enums import AuthProvider


class PlayerAuth(Base):
    __tablename__ = "player_auth"
    __table_args__ = (
        UniqueConstraint("provider", "provider_uid", name="uq_provider_provider_uid"),
    )

    auth_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id"), nullable=True)
    provider: Mapped[AuthProvider] = mapped_column(Enum(AuthProvider), nullable=False)
    provider_uid: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    id_token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player: Mapped["PlayerProfile"] = relationship(back_populates="auth")
    sessions: Mapped[list["PlayerSession"]] = relationship(back_populates="auth", cascade="all, delete-orphan")


from app.models.player_profile import PlayerProfile  # noqa: E402
from app.models.player_session import PlayerSession  # noqa: E402
