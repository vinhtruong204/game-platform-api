from sqlalchemy import Integer, String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.shop import ItemType, CurrencyType


class LuckyWheelItem(Base):
    __tablename__ = "lucky_wheel_item"
    __table_args__ = (
        UniqueConstraint("wheel_type", "slot_index", name="uq_wheel_type_slot_index"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wheel_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType, name="currencytype", create_type=False), nullable=False
    )
    slot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    item_type: Mapped[ItemType | None] = mapped_column(
        Enum(ItemType, name="itemtype", create_type=False), nullable=True
    )
    currency_reward: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shop_price: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=100, server_default="100")
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String(200), nullable=False)
