import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_stats import PlayerStats, GameMode
from app.repositories.player_stats_repository import PlayerStatsRepository
from app.schemas.player_stats import PlayerStatsCreate, PlayerStatsUpdate


class PlayerStatsService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerStatsRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerStats]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, mode: GameMode) -> PlayerStats:
        stats = await self.repo.get_by_id(player_id, mode)
        if stats is None:
            stats = PlayerStats(player_id=player_id, mode=mode)
            stats = await self.repo.create(stats)
        return stats

    async def create(self, data: PlayerStatsCreate) -> PlayerStats:
        stats = PlayerStats(**data.model_dump())
        return await self.repo.create(stats)

    async def update(self, player_id: uuid.UUID, mode: GameMode, data: PlayerStatsUpdate) -> PlayerStats:
        stats = await self.get_by_id(player_id, mode)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(stats, update_data)

    async def delete(self, player_id: uuid.UUID, mode: GameMode) -> None:
        stats = await self.get_by_id(player_id, mode)
        await self.repo.delete(stats)
