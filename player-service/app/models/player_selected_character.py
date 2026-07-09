import uuid

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PlayerSelectedCharacter(Base):
    __tablename__ = "player_selected_character"

    player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("player_profile.player_id", ondelete="CASCADE"), primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer)

    player: Mapped["PlayerProfile"] = relationship(back_populates="selected_character")


from app.models.player_profile import PlayerProfile  # noqa: E402
