from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Mode(Base):
    __tablename__ = "mode"

    mode_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    players_per_team: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    selection_weight: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    matches: Mapped[list["MatchHistory"]] = relationship(back_populates="mode")


from app.models.match_history import MatchHistory  # noqa: E402
