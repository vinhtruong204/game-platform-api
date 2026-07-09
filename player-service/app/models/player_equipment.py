import enum
import uuid

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class SlotType(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"
    melee = "melee"
    grenade = "grenade"
    character = "character"


class PlayerEquipment(Base):
    __tablename__ = "player_equipment"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    slot_type: Mapped[SlotType] = mapped_column(Enum(SlotType, name="slottype"), primary_key=True)
    weapon_id: Mapped[int] = mapped_column(Integer)

    player: Mapped["PlayerProfile"] = relationship(back_populates="equipment")


from app.models.player_profile import PlayerProfile  # noqa: E402
