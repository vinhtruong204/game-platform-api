import enum
import uuid

from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class CurrencyType(str, enum.Enum):
    gold = "gold"
    diamond = "diamond"


class PlayerCurrency(Base):
    __tablename__ = "player_currency"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    currency_type: Mapped[CurrencyType] = mapped_column(Enum(CurrencyType, name="currencytype"), primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, default=0)

    player: Mapped["PlayerProfile"] = relationship(back_populates="currencies")


from app.models.player_profile import PlayerProfile  # noqa: E402
