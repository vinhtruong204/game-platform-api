from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rank_config import RankConfig


class RankConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[RankConfig]:
        result = await self.db.execute(
            select(RankConfig).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, rank_id: int) -> RankConfig | None:
        result = await self.db.execute(
            select(RankConfig).where(RankConfig.rank_id == rank_id)
        )
        return result.scalar_one_or_none()

    async def create(self, rank_config: RankConfig) -> RankConfig:
        self.db.add(rank_config)
        await self.db.flush()
        await self.db.refresh(rank_config)
        return rank_config

    async def update(self, rank_config: RankConfig, data: dict) -> RankConfig:
        for key, value in data.items():
            setattr(rank_config, key, value)
        await self.db.flush()
        await self.db.refresh(rank_config)
        return rank_config

    async def delete(self, rank_config: RankConfig) -> None:
        await self.db.delete(rank_config)
        await self.db.flush()
