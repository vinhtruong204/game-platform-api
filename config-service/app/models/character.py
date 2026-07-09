from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Character(Base):
    __tablename__ = "character"

    character_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    character_type: Mapped[str] = mapped_column(String(50))
    hp: Mapped[int] = mapped_column(Integer)
    run_speed: Mapped[float] = mapped_column(Float)
    texture: Mapped[str] = mapped_column(String(255))
