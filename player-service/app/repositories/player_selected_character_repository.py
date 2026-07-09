import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_selected_character import PlayerSelectedCharacter


class PlayerSelectedCharacterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[PlayerSelectedCharacter]:
        result = await self.db.execute(select(PlayerSelectedCharacter))
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID) -> PlayerSelectedCharacter | None:
        result = await self.db.execute(
            select(PlayerSelectedCharacter).where(
                PlayerSelectedCharacter.player_id == player_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, selected: PlayerSelectedCharacter) -> PlayerSelectedCharacter:
        self.db.add(selected)
        await self.db.flush()
        await self.db.refresh(selected)
        return selected

    async def update(self, selected: PlayerSelectedCharacter, data: dict) -> PlayerSelectedCharacter:
        for key, value in data.items():
            setattr(selected, key, value)
        await self.db.flush()
        await self.db.refresh(selected)
        return selected

    async def delete(self, selected: PlayerSelectedCharacter) -> None:
        await self.db.delete(selected)
        await self.db.flush()
