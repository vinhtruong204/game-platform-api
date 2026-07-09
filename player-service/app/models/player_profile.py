import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PlayerProfile(Base):
    __tablename__ = "player_profile"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    current_level_id: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String(50))
    slogan: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_exp: Mapped[int] = mapped_column(Integer, default=0)
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_new_player: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    stats: Mapped[list["PlayerStats"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    currencies: Mapped[list["PlayerCurrency"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    inventory: Mapped[list["PlayerInventory"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    equipment: Mapped[list["PlayerEquipment"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    selected_character: Mapped["PlayerSelectedCharacter | None"] = relationship(back_populates="player", cascade="all, delete-orphan", uselist=False)
    achievements: Mapped[list["PlayerAchievement"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    ranks: Mapped[list["PlayerRank"]] = relationship(back_populates="player", cascade="all, delete-orphan")
    auth: Mapped["PlayerAuth | None"] = relationship(back_populates="player", cascade="all, delete-orphan", uselist=False)


from app.models.player_stats import PlayerStats  # noqa: E402
from app.models.player_currency import PlayerCurrency  # noqa: E402
from app.models.player_inventory import PlayerInventory  # noqa: E402
from app.models.player_equipment import PlayerEquipment  # noqa: E402
from app.models.player_selected_character import PlayerSelectedCharacter  # noqa: E402
from app.models.player_achievement import PlayerAchievement  # noqa: E402
from app.models.player_rank import PlayerRank  # noqa: E402
from app.models.player_auth import PlayerAuth  # noqa: E402
