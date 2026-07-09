from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Map(Base):
    __tablename__ = "map"

    map_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=False)

    matches: Mapped[list["MatchHistory"]] = relationship(back_populates="map")


from app.models.match_history import MatchHistory  # noqa: E402
