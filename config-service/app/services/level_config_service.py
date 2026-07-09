from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level_config import LevelConfig
from app.repositories.level_config_repository import LevelConfigRepository
from app.schemas.level_config import LevelConfigCreate, LevelConfigUpdate


class LevelConfigService:
    def __init__(self, db: AsyncSession):
        self.repo = LevelConfigRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[LevelConfig]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, level_id: int) -> LevelConfig:
        level_config = await self.repo.get_by_id(level_id)
        if not level_config:
            raise HTTPException(status_code=404, detail="Level config not found")
        return level_config

    async def create(self, data: LevelConfigCreate) -> LevelConfig:
        level_config = LevelConfig(**data.model_dump())
        return await self.repo.create(level_config)

    async def update(self, level_id: int, data: LevelConfigUpdate) -> LevelConfig:
        level_config = await self.get_by_id(level_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(level_config, update_data)

    async def delete(self, level_id: int) -> None:
        level_config = await self.get_by_id(level_id)
        await self.repo.delete(level_config)
