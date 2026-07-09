from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_history import MatchHistory


class MatchHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[MatchHistory]:
        result = await self.db.execute(select(MatchHistory))
        return list(result.scalars().all())

    async def get_by_id(self, match_id: int) -> MatchHistory | None:
        result = await self.db.execute(
            select(MatchHistory).where(MatchHistory.match_id == match_id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: MatchHistory) -> MatchHistory:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: MatchHistory, data: dict) -> MatchHistory:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: MatchHistory) -> None:
        await self.db.delete(entity)
        await self.db.flush()
