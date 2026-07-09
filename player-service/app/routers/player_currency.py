import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_currency import CurrencyType
from app.models.player_session import PlayerSession
from app.schemas.player_currency import PlayerCurrencyCreate, PlayerCurrencyUpdate, PlayerCurrencyResponse, CurrencyModify
from app.services.player_currency_service import PlayerCurrencyService

router = APIRouter(prefix="/player-currencies", tags=["Player Currencies"])


@router.get("/", response_model=list[PlayerCurrencyResponse])
async def get_all_currencies(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerCurrencyService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/{currency_type}", response_model=PlayerCurrencyResponse)
async def get_currency(player_id: uuid.UUID, currency_type: CurrencyType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerCurrencyService(db)
    return await service.get_by_id(player_id, currency_type)


@router.post("/", response_model=PlayerCurrencyResponse, status_code=status.HTTP_201_CREATED)
async def create_currency(data: PlayerCurrencyCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerCurrencyService(db)
    return await service.create(data)


@router.put("/{player_id}/{currency_type}", response_model=PlayerCurrencyResponse)
async def update_currency(player_id: uuid.UUID, currency_type: CurrencyType, data: PlayerCurrencyUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerCurrencyService(db)
    return await service.update(player_id, currency_type, data)


@router.patch("/{player_id}/{currency_type}/deduct", response_model=PlayerCurrencyResponse)
async def deduct_currency(player_id: uuid.UUID, currency_type: CurrencyType, data: CurrencyModify, db: AsyncSession = Depends(get_db), session: PlayerSession = Depends(get_current_player)):
    if session.player_id != player_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify another player's currency")
    service = PlayerCurrencyService(db)
    return await service.deduct_currency(player_id, currency_type, data.amount)


@router.patch("/{player_id}/{currency_type}/add", response_model=PlayerCurrencyResponse)
async def add_currency(player_id: uuid.UUID, currency_type: CurrencyType, data: CurrencyModify, db: AsyncSession = Depends(get_db), session: PlayerSession = Depends(get_current_player)):
    if session.player_id != player_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify another player's currency")
    service = PlayerCurrencyService(db)
    return await service.add_currency(player_id, currency_type, data.amount)


@router.delete("/{player_id}/{currency_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency(player_id: uuid.UUID, currency_type: CurrencyType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerCurrencyService(db)
    await service.delete(player_id, currency_type)
