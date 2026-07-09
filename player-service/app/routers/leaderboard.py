from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.leaderboard import LeaderboardMode, LeaderboardResponse
from app.services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/{mode}", response_model=LeaderboardResponse)
async def get_leaderboard(
    mode: LeaderboardMode,
    db: AsyncSession = Depends(get_db),
    _session: PlayerSession = Depends(get_current_player),
):
    service = LeaderboardService(db)
    return await service.get_leaderboard(mode)
