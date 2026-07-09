import enum
from datetime import datetime

from sqlalchemy import Integer, Float, Boolean, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ItemType(str, enum.Enum):
    weapon = "weapon"
    character = "character"
    item = "item"


class CurrencyType(str, enum.Enum):
    gold = "gold"
    diamond = "diamond"


class Shop(Base):
    __tablename__ = "shop"

    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType, name="itemtype"), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_type: Mapped[CurrencyType] = mapped_column(Enum(CurrencyType, name="currencytype"), nullable=False)
    discount: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0")
    is_today: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
