from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level_config import LevelConfig


class LevelConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[LevelConfig]:
        result = await self.db.execute(
            select(LevelConfig).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, level_id: int) -> LevelConfig | None:
        result = await self.db.execute(
            select(LevelConfig).where(LevelConfig.level_id == level_id)
        )
        return result.scalar_one_or_none()

    async def create(self, level_config: LevelConfig) -> LevelConfig:
        self.db.add(level_config)
        await self.db.flush()
        await self.db.refresh(level_config)
        return level_config

    async def update(self, level_config: LevelConfig, data: dict) -> LevelConfig:
        for key, value in data.items():
            setattr(level_config, key, value)
        await self.db.flush()
        await self.db.refresh(level_config)
        return level_config

    async def delete(self, level_config: LevelConfig) -> None:
        await self.db.delete(level_config)
        await self.db.flush()
