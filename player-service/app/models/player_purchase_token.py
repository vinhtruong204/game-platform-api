import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.player_currency import CurrencyType


class PlayerPurchaseToken(Base):
    __tablename__ = "player_purchase_tokens"
    __table_args__ = (
        Index("ix_player_purchase_tokens_token", "purchase_token", unique=True),
    )

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("player_profile.player_id", ondelete="CASCADE"),
        primary_key=True,
    )
    purchase_token: Mapped[str] = mapped_column(String(512), primary_key=True)
    sku: Mapped[str] = mapped_column(String(128), nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    credited_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType, name="currencytype"), nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["PlayerProfile"] = relationship()


from app.models.player_profile import PlayerProfile  # noqa: E402
