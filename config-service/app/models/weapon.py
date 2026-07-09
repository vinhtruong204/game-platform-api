from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Weapon(Base):
    __tablename__ = "weapon"

    weapon_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    weapon_type: Mapped[str] = mapped_column(String(50))
    damage: Mapped[int] = mapped_column(Integer)
    fire_rate: Mapped[float] = mapped_column(Float)
    image: Mapped[str] = mapped_column(String(255))
    ammo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
