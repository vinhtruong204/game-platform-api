import enum
import uuid
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class ItemType(str, enum.Enum):
    weapon = "weapon"
    character = "character"
    item = "item"


class PlayerInventory(Base):
    __tablename__ = "player_inventory"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType, name="itemtype"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    obtain_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    player: Mapped["PlayerProfile"] = relationship(back_populates="inventory")


from app.models.player_profile import PlayerProfile  # noqa: E402
