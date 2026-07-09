import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_stats import PlayerStats, GameMode


class PlayerStatsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerStats]:
        stmt = select(PlayerStats)
        if player_id is not None:
            stmt = stmt.where(PlayerStats.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, mode: GameMode) -> PlayerStats | None:
        result = await self.db.execute(
            select(PlayerStats).where(
                PlayerStats.player_id == player_id,
                PlayerStats.mode == mode,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, stats: PlayerStats) -> PlayerStats:
        self.db.add(stats)
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def update(self, stats: PlayerStats, data: dict) -> PlayerStats:
        for key, value in data.items():
            setattr(stats, key, value)
        await self.db.flush()
        await self.db.refresh(stats)
        return stats

    async def delete(self, stats: PlayerStats) -> None:
        await self.db.delete(stats)
        await self.db.flush()
