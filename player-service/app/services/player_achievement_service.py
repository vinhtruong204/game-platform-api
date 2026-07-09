import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_achievement import PlayerAchievement
from app.repositories.player_achievement_repository import PlayerAchievementRepository
from app.schemas.player_achievement import PlayerAchievementCreate, PlayerAchievementUpdate


class PlayerAchievementService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerAchievementRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerAchievement]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, achievement_id: int) -> PlayerAchievement:
        achievement = await self.repo.get_by_id(player_id, achievement_id)
        if not achievement:
            raise HTTPException(status_code=404, detail="Player achievement not found")
        return achievement

    async def create(self, data: PlayerAchievementCreate) -> PlayerAchievement:
        achievement = PlayerAchievement(**data.model_dump())
        return await self.repo.create(achievement)

    async def update(self, player_id: uuid.UUID, achievement_id: int, data: PlayerAchievementUpdate) -> PlayerAchievement:
        achievement = await self.get_by_id(player_id, achievement_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(achievement, update_data)

    async def delete(self, player_id: uuid.UUID, achievement_id: int) -> None:
        achievement = await self.get_by_id(player_id, achievement_id)
        await self.repo.delete(achievement)
