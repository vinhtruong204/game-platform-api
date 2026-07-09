import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.matchmaking import MatchmakingJoinRequest
from app.services.matchmaking_service import MatchmakingService

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])


@router.post("/join")
async def join_queue(
    data: MatchmakingJoinRequest,
    db: AsyncSession = Depends(get_db),
    player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = MatchmakingService(db)
    return await service.join(player_id, data)


@router.get("/status")
async def get_status(
    db: AsyncSession = Depends(get_db),
    player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = MatchmakingService(db)
    return await service.status(player_id)


@router.delete("/leave")
async def leave_queue(
    db: AsyncSession = Depends(get_db),
    player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = MatchmakingService(db)
    return await service.leave(player_id)
