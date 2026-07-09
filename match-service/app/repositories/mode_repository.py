from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mode import Mode


class ModeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Mode]:
        result = await self.db.execute(select(Mode))
        return list(result.scalars().all())

    async def get_by_id(self, mode_id: int) -> Mode | None:
        result = await self.db.execute(
            select(Mode).where(Mode.mode_id == mode_id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: Mode) -> Mode:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: Mode, data: dict) -> Mode:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: Mode) -> None:
        await self.db.delete(entity)
        await self.db.flush()
