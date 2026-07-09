from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rank_config import RankConfig
from app.repositories.rank_config_repository import RankConfigRepository
from app.schemas.rank_config import RankConfigCreate, RankConfigUpdate


class RankConfigService:
    def __init__(self, db: AsyncSession):
        self.repo = RankConfigRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[RankConfig]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, rank_id: int) -> RankConfig:
        rank_config = await self.repo.get_by_id(rank_id)
        if not rank_config:
            raise HTTPException(status_code=404, detail="Rank config not found")
        return rank_config

    async def create(self, data: RankConfigCreate) -> RankConfig:
        rank_config = RankConfig(**data.model_dump())
        return await self.repo.create(rank_config)

    async def update(self, rank_id: int, data: RankConfigUpdate) -> RankConfig:
        rank_config = await self.get_by_id(rank_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(rank_config, update_data)

    async def delete(self, rank_id: int) -> None:
        rank_config = await self.get_by_id(rank_id)
        await self.repo.delete(rank_config)
