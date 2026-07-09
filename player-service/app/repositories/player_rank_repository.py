import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_rank import PlayerRank


class PlayerRankRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerRank]:
        stmt = select(PlayerRank)
        if player_id is not None:
            stmt = stmt.where(PlayerRank.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, season_id: int) -> PlayerRank | None:
        result = await self.db.execute(
            select(PlayerRank).where(
                PlayerRank.player_id == player_id,
                PlayerRank.season_id == season_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, player_rank: PlayerRank) -> PlayerRank:
        self.db.add(player_rank)
        await self.db.flush()
        await self.db.refresh(player_rank)
        return player_rank

    async def update(self, player_rank: PlayerRank, data: dict) -> PlayerRank:
        for key, value in data.items():
            setattr(player_rank, key, value)
        await self.db.flush()
        await self.db.refresh(player_rank)
        return player_rank

    async def delete(self, player_rank: PlayerRank) -> None:
        await self.db.delete(player_rank)
        await self.db.flush()
