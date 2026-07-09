from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class RankConfig(Base):
    __tablename__ = "rank_config"

    rank_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    min_point: Mapped[int] = mapped_column(Integer)
    max_point: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(255))
