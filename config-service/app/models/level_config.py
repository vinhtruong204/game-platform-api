from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class LevelConfig(Base):
    __tablename__ = "level_config"

    level_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    min_exp: Mapped[int] = mapped_column(Integer)
    max_exp: Mapped[int] = mapped_column(Integer)
    reward_gold: Mapped[int] = mapped_column(Integer)
    reward_diamond: Mapped[int] = mapped_column(Integer)
