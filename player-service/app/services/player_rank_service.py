import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_rank import PlayerRank
from app.repositories.player_rank_repository import PlayerRankRepository
from app.schemas.player_rank import PlayerRankCreate, PlayerRankUpdate


class PlayerRankService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerRankRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerRank]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, season_id: int) -> PlayerRank:
        player_rank = await self.repo.get_by_id(player_id, season_id)
        if not player_rank:
            raise HTTPException(status_code=404, detail="Player rank not found")
        return player_rank

    async def create(self, data: PlayerRankCreate) -> PlayerRank:
        player_rank = PlayerRank(**data.model_dump())
        return await self.repo.create(player_rank)

    async def update(self, player_id: uuid.UUID, season_id: int, data: PlayerRankUpdate) -> PlayerRank:
        player_rank = await self.get_by_id(player_id, season_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(player_rank, update_data)

    async def delete(self, player_id: uuid.UUID, season_id: int) -> None:
        player_rank = await self.get_by_id(player_id, season_id)
        await self.repo.delete(player_rank)
