import random
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.map import Map
from app.models.match_history import MatchHistory, MatchStatus
from app.models.match_player import MatchPlayer, MatchResult
from app.models.matchmaking_queue import MatchmakingQueue, QueueStatus
from app.models.mode import Mode
from app.repositories.matchmaking_queue_repository import MatchmakingQueueRepository
from app.schemas.matchmaking import MatchmakingJoinRequest

POINT_RANGE = 500
POINT_RANGE_RELAXED = 1000
WAIT_THRESHOLD_SECS = 10
RELAX_THRESHOLD_SECS = 30
NORMAL_RELAX_WAIT_SECS = 5
STALE_TIMEOUT_MINS = 10


class MatchmakingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MatchmakingQueueRepository(db)

    async def join(self, player_id: uuid.UUID, request: MatchmakingJoinRequest) -> dict:
        existing = await self.repo.get_waiting_by_player(player_id)
        if existing:
            raise HTTPException(status_code=409, detail="Already in queue")

        await self.repo.cleanup_matched_by_player(player_id)
        await self.repo.cleanup_stale(STALE_TIMEOUT_MINS)

        game_mode = request.game_mode if request.game_mode in ("rank", "normal") else "rank"
        players_per_team = max(1, min(request.players_per_team, 2))
        mode_id = None
        if game_mode == "normal":
            mode = await self._resolve_mode(game_mode, players_per_team, request.mode_id)
            mode_id = mode.mode_id
        else:
            await self._resolve_ranked_mode(players_per_team)
        map_ = await self._resolve_map(request.map_id)

        entry = MatchmakingQueue(
            player_id=player_id,
            rank_point=request.rank_point,
            game_mode=game_mode,
            map_id=map_.map_id if game_mode == "normal" else None,
            mode_id=mode_id,
            players_per_team=players_per_team,
            status=QueueStatus.waiting,
        )
        entry = await self.repo.create(entry)

        match_result = await self._try_create_match(entry)
        if match_result:
            return match_result

        position = await self.repo.get_waiting_position(player_id)
        return {
            "status": "queued",
            "queue_id": entry.queue_id,
            "player_id": entry.player_id,
            "position": position,
            "joined_at": entry.joined_at,
        }

    async def status(self, player_id: uuid.UUID) -> dict:
        entry = await self.repo.get_latest_by_player(player_id)
        if not entry:
            return {"status": "none"}

        if entry.status == QueueStatus.matched:
            return await self._build_match_response(entry, "matched")

        # Re-attempt matching on every poll
        match_result = await self._try_create_match(entry)
        if match_result:
            return match_result

        now = datetime.utcnow()
        wait_seconds = (now - entry.joined_at).total_seconds()
        position = await self.repo.get_waiting_position(player_id)
        return {
            "status": "waiting",
            "queue_id": entry.queue_id,
            "position": position,
            "wait_seconds": round(wait_seconds, 1),
            "joined_at": entry.joined_at,
        }

    async def leave(self, player_id: uuid.UUID) -> dict:
        entry = await self.repo.get_waiting_by_player(player_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Not in queue")

        await self.repo.delete(entry)
        return {"status": "left", "player_id": player_id}

    async def _try_create_match(self, new_entry: MatchmakingQueue) -> dict | None:
        now = datetime.utcnow()

        candidates = await self.repo.get_candidates_for_update(
            new_entry.rank_point,
            POINT_RANGE,
            new_entry.game_mode,
            new_entry.players_per_team,
            new_entry.map_id,
            new_entry.mode_id,
        )

        any_relaxed = any(
            (now - c.joined_at).total_seconds() > RELAX_THRESHOLD_SECS
            for c in candidates
        )
        if any_relaxed:
            candidates = await self.repo.get_candidates_for_update(
                new_entry.rank_point,
                POINT_RANGE_RELAXED,
                new_entry.game_mode,
                new_entry.players_per_team,
                new_entry.map_id,
                new_entry.mode_id,
            )

        if (
            len(candidates) < 2
            and new_entry.game_mode == "normal"
            and (now - new_entry.joined_at).total_seconds() >= NORMAL_RELAX_WAIT_SECS
        ):
            candidates = await self.repo.get_candidates_for_update(
                new_entry.rank_point,
                POINT_RANGE_RELAXED,
                new_entry.game_mode,
                new_entry.players_per_team,
                ignore_map_mode=True,
            )

        if new_entry.players_per_team == 2 and len(candidates) >= 4:
            sorted_by_rank = sorted(
                candidates, key=lambda c: abs(c.rank_point - new_entry.rank_point)
            )
            picked = sorted_by_rank[:4]
            return await self._create_match(picked, players_per_team=2)

        any_waited = any(
            (now - c.joined_at).total_seconds() > WAIT_THRESHOLD_SECS
            for c in candidates
        )
        if len(candidates) >= 2 and (new_entry.game_mode == "normal" or any_waited):
            sorted_by_rank = sorted(
                candidates,
                key=lambda c: (
                    abs(c.rank_point - new_entry.rank_point),
                    c.joined_at,
                ),
            )
            picked = sorted_by_rank[:2]
            return await self._create_match(picked, players_per_team=1)

        return None

    async def _create_match(
        self, players: list[MatchmakingQueue], players_per_team: int
    ) -> dict:
        first_player = players[0]
        if first_player.game_mode == "rank":
            mode = await self._resolve_ranked_mode(players_per_team)
        else:
            mode = await self._resolve_mode(
                first_player.game_mode, players_per_team, first_player.mode_id
            )
        map_ = await self._resolve_map(first_player.map_id)

        match = MatchHistory(
            map_id=map_.map_id,
            mode_id=mode.mode_id,
            start_time=datetime.utcnow(),
            end_time=None,
            status=MatchStatus.pending,
            season_id=1 if first_player.game_mode == "rank" else None,
        )
        self.db.add(match)
        await self.db.flush()
        await self.db.refresh(match)

        teams = self._assign_teams(players, players_per_team)

        player_infos = []
        for queue_entry, team_id in teams:
            match_player = MatchPlayer(
                match_id=match.match_id,
                player_id=queue_entry.player_id,
                team_id=team_id,
                kill=0,
                dead=0,
                assists=0,
                result=MatchResult.win,
                score=0,
                exp_earned=0,
                reward_gold=0,
            )
            self.db.add(match_player)
            player_infos.append(
                {
                    "player_id": queue_entry.player_id,
                    "team_id": team_id,
                }
            )

        now = datetime.utcnow()
        for queue_entry in players:
            queue_entry.status = QueueStatus.matched
            queue_entry.matched_match_id = match.match_id
            queue_entry.matched_at = now

        await self.db.flush()

        return {
            "status": "match_found",
            "match_id": match.match_id,
            "mode_id": mode.mode_id,
            "mode_name": mode.name,
            "mode_code": mode.code,
            "map_id": map_.map_id,
            "map_name": map_.name,
            "players_per_team": players_per_team,
            "players": player_infos,
        }

    def _assign_teams(
        self, players: list[MatchmakingQueue], players_per_team: int
    ) -> list[tuple[MatchmakingQueue, int]]:
        if len(players) == 1:
            return [(players[0], 1)]

        if players_per_team == 1:
            return [(players[0], 1), (players[1], 2)]

        sorted_players = sorted(players, key=lambda p: p.rank_point, reverse=True)
        return [
            (sorted_players[0], 1),
            (sorted_players[3], 1),
            (sorted_players[1], 2),
            (sorted_players[2], 2),
        ]

    async def _resolve_mode(
        self, game_mode: str, players_per_team: int, preferred_mode_id: int | None
    ) -> Mode:
        if preferred_mode_id:
            result = await self.db.execute(
                select(Mode).where(
                    Mode.mode_id == preferred_mode_id,
                    Mode.type == game_mode,
                    Mode.players_per_team == players_per_team,
                )
            )
            mode = result.scalar_one_or_none()
            if mode:
                return mode

        result = await self.db.execute(
            select(Mode).where(
                Mode.type == game_mode,
                Mode.players_per_team == players_per_team,
            )
        )
        modes = list(result.scalars().all())
        if not modes:
            result = await self.db.execute(
                select(Mode).where(Mode.players_per_team == players_per_team)
            )
            modes = list(result.scalars().all())
        if not modes:
            result = await self.db.execute(select(Mode))
            modes = list(result.scalars().all())
        if not modes:
            raise HTTPException(status_code=500, detail="No game modes configured")
        return random.choice(modes)

    async def _resolve_ranked_mode(self, players_per_team: int) -> Mode:
        result = await self.db.execute(
            select(Mode).where(
                Mode.type == "rank",
                Mode.players_per_team == players_per_team,
            )
        )
        modes = list(result.scalars().all())
        if not modes:
            return await self._resolve_mode("rank", players_per_team, None)

        total_weight = sum(max(0, int(mode.selection_weight or 0)) for mode in modes)
        if total_weight <= 0:
            return random.choice(modes)

        pick = random.uniform(0, total_weight)
        current = 0.0
        for mode in modes:
            current += max(0, int(mode.selection_weight or 0))
            if pick <= current:
                return mode

        return modes[-1]

    async def _resolve_map(self, preferred_map_id: int | None) -> Map:
        if preferred_map_id:
            result = await self.db.execute(
                select(Map).where(Map.map_id == preferred_map_id)
            )
            map_ = result.scalar_one_or_none()
            if map_:
                return map_

        result = await self.db.execute(select(Map))
        maps = list(result.scalars().all())
        if not maps:
            raise HTTPException(status_code=500, detail="No maps configured")
        return random.choice(maps)

    async def _build_match_response(
        self, entry: MatchmakingQueue, status_str: str
    ) -> dict:
        match_id = entry.matched_match_id

        match_result = await self.db.execute(
            select(MatchHistory).where(MatchHistory.match_id == match_id)
        )
        match = match_result.scalar_one_or_none()
        if not match:
            return {"status": "none"}

        mode_result = await self.db.execute(
            select(Mode).where(Mode.mode_id == match.mode_id)
        )
        mode = mode_result.scalar_one()

        map_result = await self.db.execute(
            select(Map).where(Map.map_id == match.map_id)
        )
        map_ = map_result.scalar_one()

        players_result = await self.db.execute(
            select(MatchPlayer).where(MatchPlayer.match_id == match_id)
        )
        match_players = list(players_result.scalars().all())

        return {
            "status": status_str,
            "match_id": match_id,
            "mode_id": mode.mode_id,
            "mode_name": mode.name,
            "mode_code": mode.code,
            "map_id": map_.map_id,
            "map_name": map_.name,
            "players_per_team": mode.players_per_team,
            "players": [
                {"player_id": mp.player_id, "team_id": mp.team_id}
                for mp in match_players
            ],
        }
