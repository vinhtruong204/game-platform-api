import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_profile import PlayerProfile
from app.repositories.player_profile_repository import PlayerProfileRepository
from app.schemas.player_profile import PlayerProfileCreate, PlayerProfileUpdate


class PlayerProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerProfileRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[PlayerProfile]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, player_id: uuid.UUID) -> PlayerProfile:
        player = await self.repo.get_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player

    async def create(self, data: PlayerProfileCreate) -> PlayerProfile:
        player = PlayerProfile(**data.model_dump())
        return await self.repo.create(player)

    async def update(self, player_id: uuid.UUID, data: PlayerProfileUpdate) -> PlayerProfile:
        player = await self.get_by_id(player_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(player, update_data)

    async def delete(self, player_id: uuid.UUID) -> None:
        player = await self.get_by_id(player_id)
        await self.repo.delete(player)
