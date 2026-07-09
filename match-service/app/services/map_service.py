from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.map import Map
from app.repositories.map_repository import MapRepository
from app.schemas.map import MapCreate, MapUpdate


class MapService:
    def __init__(self, db: AsyncSession):
        self.repo = MapRepository(db)

    async def get_all(self) -> list[Map]:
        return await self.repo.get_all()

    async def get_by_id(self, map_id: int) -> Map:
        entity = await self.repo.get_by_id(map_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Map not found")
        return entity

    async def create(self, data: MapCreate) -> Map:
        entity = Map(**data.model_dump())
        return await self.repo.create(entity)

    async def update(self, map_id: int, data: MapUpdate) -> Map:
        entity = await self.get_by_id(map_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(entity, update_data)

    async def delete(self, map_id: int) -> None:
        entity = await self.get_by_id(map_id)
        await self.repo.delete(entity)
