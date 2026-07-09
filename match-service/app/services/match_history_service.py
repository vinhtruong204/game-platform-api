from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_history import MatchHistory
from app.repositories.match_history_repository import MatchHistoryRepository
from app.schemas.match_history import MatchHistoryCreate, MatchHistoryUpdate


class MatchHistoryService:
    def __init__(self, db: AsyncSession):
        self.repo = MatchHistoryRepository(db)

    async def get_all(self) -> list[MatchHistory]:
        return await self.repo.get_all()

    async def get_by_id(self, match_id: int) -> MatchHistory:
        entity = await self.repo.get_by_id(match_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Match not found")
        return entity

    async def create(self, data: MatchHistoryCreate) -> MatchHistory:
        entity = MatchHistory(**data.model_dump())
        return await self.repo.create(entity)

    async def update(self, match_id: int, data: MatchHistoryUpdate) -> MatchHistory:
        entity = await self.get_by_id(match_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(entity, update_data)

    async def delete(self, match_id: int) -> None:
        entity = await self.get_by_id(match_id)
        await self.repo.delete(entity)
