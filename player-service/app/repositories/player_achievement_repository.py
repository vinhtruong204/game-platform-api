import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_achievement import PlayerAchievement


class PlayerAchievementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerAchievement]:
        stmt = select(PlayerAchievement)
        if player_id is not None:
            stmt = stmt.where(PlayerAchievement.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, achievement_id: int) -> PlayerAchievement | None:
        result = await self.db.execute(
            select(PlayerAchievement).where(
                PlayerAchievement.player_id == player_id,
                PlayerAchievement.achievement_id == achievement_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, achievement: PlayerAchievement) -> PlayerAchievement:
        self.db.add(achievement)
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement

    async def update(self, achievement: PlayerAchievement, data: dict) -> PlayerAchievement:
        for key, value in data.items():
            setattr(achievement, key, value)
        await self.db.flush()
        await self.db.refresh(achievement)
        return achievement

    async def delete(self, achievement: PlayerAchievement) -> None:
        await self.db.delete(achievement)
        await self.db.flush()
