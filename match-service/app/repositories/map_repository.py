from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.map import Map


class MapRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Map]:
        result = await self.db.execute(select(Map))
        return list(result.scalars().all())

    async def get_by_id(self, map_id: int) -> Map | None:
        result = await self.db.execute(
            select(Map).where(Map.map_id == map_id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: Map) -> Map:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: Map, data: dict) -> Map:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: Map) -> None:
        await self.db.delete(entity)
        await self.db.flush()
