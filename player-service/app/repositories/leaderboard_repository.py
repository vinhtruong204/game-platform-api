from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_profile import PlayerProfile
from app.models.player_rank import PlayerRank
from app.models.player_stats import PlayerStats, GameMode
from app.models.player_inventory import PlayerInventory, ItemType


class LeaderboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_ranking_leaderboard(self, season_id: int = 1, limit: int = 6):
        stmt = (
            select(
                PlayerProfile.name,
                PlayerRank.rank_id,
                PlayerRank.current_point,
                PlayerStats.number_games_win,
                PlayerStats.total_game,
                PlayerStats.kill,
                PlayerStats.dead,
            )
            .join(PlayerRank, PlayerProfile.player_id == PlayerRank.player_id)
            .join(PlayerStats, PlayerProfile.player_id == PlayerStats.player_id)
            .where(PlayerRank.season_id == season_id)
            .where(PlayerStats.mode == GameMode.rank)
            .order_by(PlayerRank.current_point.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_normal_leaderboard(self, limit: int = 6):
        stmt = (
            select(
                PlayerProfile.name,
                PlayerStats.number_games_win,
                PlayerStats.total_game,
                PlayerStats.kill,
                PlayerStats.dead,
            )
            .join(PlayerStats, PlayerProfile.player_id == PlayerStats.player_id)
            .where(PlayerStats.mode == GameMode.normal)
            .order_by(PlayerStats.number_games_win.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_collector_leaderboard(self, limit: int = 6):
        stmt = (
            select(
                PlayerProfile.name,
                func.count(case((PlayerInventory.item_type == ItemType.weapon, 1))).label("weapon_count"),
                func.count(case((PlayerInventory.item_type == ItemType.item, 1))).label("item_count"),
                func.count(case((PlayerInventory.item_type == ItemType.character, 1))).label("character_count"),
                func.count().label("total_items"),
            )
            .join(PlayerInventory, PlayerProfile.player_id == PlayerInventory.player_id)
            .group_by(PlayerProfile.player_id, PlayerProfile.name)
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.all()
