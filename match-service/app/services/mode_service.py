from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mode import Mode
from app.repositories.mode_repository import ModeRepository
from app.schemas.mode import ModeCreate, ModeUpdate


class ModeService:
    def __init__(self, db: AsyncSession):
        self.repo = ModeRepository(db)

    async def get_all(self) -> list[Mode]:
        return await self.repo.get_all()

    async def get_by_id(self, mode_id: int) -> Mode:
        entity = await self.repo.get_by_id(mode_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Mode not found")
        return entity

    async def create(self, data: ModeCreate) -> Mode:
        entity = Mode(**data.model_dump())
        return await self.repo.create(entity)

    async def update(self, mode_id: int, data: ModeUpdate) -> Mode:
        entity = await self.get_by_id(mode_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(entity, update_data)

    async def delete(self, mode_id: int) -> None:
        entity = await self.get_by_id(mode_id)
        await self.repo.delete(entity)
