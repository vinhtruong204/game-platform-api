import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_player import MatchPlayer, MatchResult


class MatchPlayerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, match_id: int | None = None) -> list[MatchPlayer]:
        stmt = select(MatchPlayer)
        if match_id is not None:
            stmt = stmt.where(MatchPlayer.match_id == match_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_rank_results_desc(self, player_id: uuid.UUID) -> list[MatchResult]:
        from app.models.match_history import MatchHistory
        from app.models.mode import Mode
        stmt = (
            select(MatchPlayer.result)
            .join(MatchHistory, MatchPlayer.match_id == MatchHistory.match_id)
            .join(Mode, MatchHistory.mode_id == Mode.mode_id)
            .where(MatchPlayer.player_id == player_id)
            .where(Mode.type == "rank")
            .order_by(MatchHistory.match_id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, match_id: int, player_id: uuid.UUID) -> MatchPlayer | None:
        result = await self.db.execute(
            select(MatchPlayer).where(
                MatchPlayer.match_id == match_id,
                MatchPlayer.player_id == player_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, entity: MatchPlayer) -> MatchPlayer:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: MatchPlayer, data: dict) -> MatchPlayer:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: MatchPlayer) -> None:
        await self.db.delete(entity)
        await self.db.flush()
