from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.repositories.achievement_repository import AchievementRepository
from app.schemas.achievement import AchievementCreate, AchievementUpdate


class AchievementService:
    def __init__(self, db: AsyncSession):
        self.repo = AchievementRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Achievement]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, achievement_id: int) -> Achievement:
        achievement = await self.repo.get_by_id(achievement_id)
        if not achievement:
            raise HTTPException(status_code=404, detail="Achievement not found")
        return achievement

    async def create(self, data: AchievementCreate) -> Achievement:
        achievement = Achievement(**data.model_dump())
        return await self.repo.create(achievement)

    async def update(self, achievement_id: int, data: AchievementUpdate) -> Achievement:
        achievement = await self.get_by_id(achievement_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(achievement, update_data)

    async def delete(self, achievement_id: int) -> None:
        achievement = await self.get_by_id(achievement_id)
        await self.repo.delete(achievement)
