import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.player_profile import PlayerProfileCreate, PlayerProfileUpdate, PlayerProfileResponse
from app.services.player_profile_service import PlayerProfileService

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/", response_model=list[PlayerProfileResponse])
async def get_all_players(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerProfileService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{player_id}", response_model=PlayerProfileResponse)
async def get_player(player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerProfileService(db)
    return await service.get_by_id(player_id)


@router.post("/", response_model=PlayerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_player(data: PlayerProfileCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerProfileService(db)
    return await service.create(data)


@router.put("/{player_id}", response_model=PlayerProfileResponse)
async def update_player(player_id: uuid.UUID, data: PlayerProfileUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerProfileService(db)
    return await service.update(player_id, data)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerProfileService(db)
    await service.delete(player_id)
