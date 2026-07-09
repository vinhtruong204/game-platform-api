from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement


class AchievementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Achievement]:
        result = await self.db.execute(
            select(Achievement).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, achievement_id: int) -> Achievement | None:
        result = await self.db.execute(
            select(Achievement).where(Achievement.achievement_id == achievement_id)
        )
        return result.scalar_one_or_none()

    async def create(self, achievement: Achievement) -> Achievement:
        self.db.add(achievement)
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement

    async def update(self, achievement: Achievement, data: dict) -> Achievement:
        for key, value in data.items():
            setattr(achievement, key, value)
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement

    async def delete(self, achievement: Achievement) -> None:
        await self.db.delete(achievement)
        await self.db.flush()
