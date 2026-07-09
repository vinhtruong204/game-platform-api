from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.purchase import (
    GooglePurchaseVerifyRequest,
    GooglePurchaseVerifyResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def purchase_item(
    data: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
    session: PlayerSession = Depends(get_current_player),
):
    service = PurchaseService(db)
    return await service.purchase(session.player_id, data)


@router.post("/google-verify", response_model=GooglePurchaseVerifyResponse)
async def verify_google_purchase(
    data: GooglePurchaseVerifyRequest,
    db: AsyncSession = Depends(get_db),
    session: PlayerSession = Depends(get_current_player),
):
    service = PurchaseService(db)
    return await service.verify_google_purchase(session.player_id, data)
