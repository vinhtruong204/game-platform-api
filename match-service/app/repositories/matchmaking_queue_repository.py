import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.matchmaking_queue import MatchmakingQueue, QueueStatus


class MatchmakingQueueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_waiting_by_player(self, player_id: uuid.UUID) -> MatchmakingQueue | None:
        result = await self.db.execute(
            select(MatchmakingQueue).where(
                MatchmakingQueue.player_id == player_id,
                MatchmakingQueue.status == QueueStatus.waiting,
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_by_player(self, player_id: uuid.UUID) -> MatchmakingQueue | None:
        result = await self.db.execute(
            select(MatchmakingQueue)
            .where(MatchmakingQueue.player_id == player_id)
            .order_by(MatchmakingQueue.queue_id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_candidates_for_update(
        self,
        rank_point: int,
        point_range: int,
        game_mode: str,
        players_per_team: int,
        map_id: int | None = None,
        mode_id: int | None = None,
        ignore_map_mode: bool = False,
    ) -> list[MatchmakingQueue]:
        filters = [
            MatchmakingQueue.status == QueueStatus.waiting,
            MatchmakingQueue.game_mode == game_mode,
            MatchmakingQueue.players_per_team == players_per_team,
            MatchmakingQueue.rank_point.between(
                rank_point - point_range, rank_point + point_range
            ),
        ]
        if not ignore_map_mode:
            if map_id is None:
                filters.append(MatchmakingQueue.map_id.is_(None))
            else:
                filters.append(MatchmakingQueue.map_id == map_id)

            if mode_id is None:
                filters.append(MatchmakingQueue.mode_id.is_(None))
            else:
                filters.append(MatchmakingQueue.mode_id == mode_id)

        result = await self.db.execute(
            select(MatchmakingQueue)
            .where(and_(*filters))
            .order_by(MatchmakingQueue.joined_at)
            .with_for_update()
        )
        return list(result.scalars().all())

    async def get_waiting_position(self, player_id: uuid.UUID) -> int:
        player_entry = (
            select(MatchmakingQueue)
            .where(MatchmakingQueue.player_id == player_id)
            .limit(1)
            .subquery()
        )
        filters = [
            MatchmakingQueue.status == QueueStatus.waiting,
            MatchmakingQueue.game_mode == player_entry.c.game_mode,
            MatchmakingQueue.players_per_team == player_entry.c.players_per_team,
            MatchmakingQueue.joined_at <= player_entry.c.joined_at,
        ]
        filters.append(
            or_(
                MatchmakingQueue.map_id == player_entry.c.map_id,
                and_(
                    MatchmakingQueue.map_id.is_(None),
                    player_entry.c.map_id.is_(None),
                ),
            )
        )
        filters.append(
            or_(
                MatchmakingQueue.mode_id == player_entry.c.mode_id,
                and_(
                    MatchmakingQueue.mode_id.is_(None),
                    player_entry.c.mode_id.is_(None),
                ),
            )
        )

        result = await self.db.execute(
            select(func.count())
            .select_from(MatchmakingQueue)
            .where(and_(*filters))
        )
        return result.scalar_one()

    async def cleanup_matched_by_player(self, player_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(MatchmakingQueue).where(
                MatchmakingQueue.player_id == player_id,
                MatchmakingQueue.status == QueueStatus.matched,
            )
        )
        await self.db.flush()

    async def cleanup_stale(self, timeout_minutes: int = 10) -> None:
        cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        await self.db.execute(
            delete(MatchmakingQueue).where(
                MatchmakingQueue.status == QueueStatus.waiting,
                MatchmakingQueue.joined_at < cutoff,
            )
        )
        await self.db.flush()

    async def create(self, entity: MatchmakingQueue) -> MatchmakingQueue:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: MatchmakingQueue, data: dict) -> MatchmakingQueue:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: MatchmakingQueue) -> None:
        await self.db.delete(entity)
        await self.db.flush()
