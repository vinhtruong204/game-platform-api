from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.spin import SpinRequest, SpinResponse
from app.services.spin_service import SpinService

router = APIRouter(prefix="/spins", tags=["Lucky Wheel Spins"])


@router.post("/", response_model=SpinResponse, status_code=status.HTTP_201_CREATED)
async def spin(
    data: SpinRequest,
    db: AsyncSession = Depends(get_db),
    session: PlayerSession = Depends(get_current_player),
):
    service = SpinService(db)
    return await service.spin(session.player_id, data)
