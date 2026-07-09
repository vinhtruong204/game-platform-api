import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_profile import PlayerProfile


class PlayerProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[PlayerProfile]:
        result = await self.db.execute(
            select(PlayerProfile).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID) -> PlayerProfile | None:
        result = await self.db.execute(
            select(PlayerProfile).where(PlayerProfile.player_id == player_id)
        )
        return result.scalar_one_or_none()

    async def create(self, player: PlayerProfile) -> PlayerProfile:
        self.db.add(player)
        await self.db.flush()
        await self.db.refresh(player)
        return player

    async def update(self, player: PlayerProfile, data: dict) -> PlayerProfile:
        for key, value in data.items():
            setattr(player, key, value)
        await self.db.flush()
        await self.db.refresh(player)
        return player

    async def delete(self, player: PlayerProfile) -> None:
        await self.db.delete(player)
        await self.db.flush()
