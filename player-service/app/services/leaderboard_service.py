from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.leaderboard_repository import LeaderboardRepository
from app.schemas.leaderboard import LeaderboardMode, LeaderboardEntry, LeaderboardResponse


RANK_NAMES = {
    1: "Bronze",
    2: "Silver",
    3: "Gold",
    4: "Platinum",
    5: "Diamond",
    6: "Master",
}


class LeaderboardService:
    def __init__(self, db: AsyncSession):
        self.repo = LeaderboardRepository(db)

    async def get_leaderboard(self, mode: LeaderboardMode) -> LeaderboardResponse:
        if mode == LeaderboardMode.ranking:
            entries = await self._build_ranking_entries()
        elif mode == LeaderboardMode.normal:
            entries = await self._build_normal_entries()
        else:
            entries = await self._build_collector_entries()

        return LeaderboardResponse(mode=mode, entries=entries)

    async def _build_ranking_entries(self) -> list[LeaderboardEntry]:
        rows = await self.repo.get_ranking_leaderboard()
        entries = []
        for i, row in enumerate(rows, start=1):
            entries.append(LeaderboardEntry(
                position=i,
                player_name=row.name,
                win_rate=self._calc_win_rate(row.number_games_win, row.total_game),
                kda=self._calc_kda(row.kill, row.dead),
                rank_name=RANK_NAMES.get(row.rank_id, "Unknown"),
            ))
        return entries

    async def _build_normal_entries(self) -> list[LeaderboardEntry]:
        rows = await self.repo.get_normal_leaderboard()
        entries = []
        for i, row in enumerate(rows, start=1):
            entries.append(LeaderboardEntry(
                position=i,
                player_name=row.name,
                win_rate=self._calc_win_rate(row.number_games_win, row.total_game),
                kda=self._calc_kda(row.kill, row.dead),
                total_game=row.total_game,
            ))
        return entries

    async def _build_collector_entries(self) -> list[LeaderboardEntry]:
        rows = await self.repo.get_collector_leaderboard()
        entries = []
        for i, row in enumerate(rows, start=1):
            entries.append(LeaderboardEntry(
                position=i,
                player_name=row.name,
                weapon_count=row.weapon_count,
                item_count=row.item_count,
                character_count=row.character_count,
                total_items=row.total_items,
            ))
        return entries

    @staticmethod
    def _calc_win_rate(wins: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round((wins / total) * 100, 1)

    @staticmethod
    def _calc_kda(kills: int, deaths: int) -> float:
        if deaths <= 0:
            return float(kills)
        return round(kills / deaths, 2)
