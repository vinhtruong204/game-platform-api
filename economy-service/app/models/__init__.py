from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.shop import Shop  # noqa: E402
from app.models.lucky_wheel_item import LuckyWheelItem  # noqa: E402

__all__ = [
    "Base",
    "Shop",
    "LuckyWheelItem",
]
