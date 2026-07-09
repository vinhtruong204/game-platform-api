import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_player import MatchPlayer, MatchResult
from app.repositories.match_player_repository import MatchPlayerRepository
from app.schemas.match_player import MatchPlayerCreate, MatchPlayerUpdate


class MatchPlayerService:
    def __init__(self, db: AsyncSession):
        self.repo = MatchPlayerRepository(db)

    async def get_all(self, match_id: int | None = None) -> list[MatchPlayer]:
        return await self.repo.get_all(match_id=match_id)

    async def get_by_id(self, match_id: int, player_id: uuid.UUID) -> MatchPlayer:
        entity = await self.repo.get_by_id(match_id, player_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Match player not found")
        return entity

    async def create(self, data: MatchPlayerCreate) -> MatchPlayer:
        entity = MatchPlayer(**data.model_dump())
        return await self.repo.create(entity)

    async def update(self, match_id: int, player_id: uuid.UUID, data: MatchPlayerUpdate) -> MatchPlayer:
        entity = await self.get_by_id(match_id, player_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(entity, update_data)

    async def delete(self, match_id: int, player_id: uuid.UUID) -> None:
        entity = await self.get_by_id(match_id, player_id)
        await self.repo.delete(entity)

    async def get_winning_streak(self, player_id: uuid.UUID) -> int:
        results = await self.repo.get_rank_results_desc(player_id)
        streak = 0
        for r in results:
            if r == MatchResult.win:
                streak += 1
            else:
                break
        return streak
