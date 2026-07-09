import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.models.player_stats import GameMode
from app.schemas.player_stats import PlayerStatsCreate, PlayerStatsUpdate, PlayerStatsResponse
from app.services.player_stats_service import PlayerStatsService

router = APIRouter(prefix="/player-stats", tags=["Player Stats"])


@router.get("/", response_model=list[PlayerStatsResponse])
async def get_all_stats(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerStatsService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/{mode}", response_model=PlayerStatsResponse)
async def get_stats(player_id: uuid.UUID, mode: GameMode, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerStatsService(db)
    return await service.get_by_id(player_id, mode)


@router.post("/", response_model=PlayerStatsResponse, status_code=status.HTTP_201_CREATED)
async def create_stats(data: PlayerStatsCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerStatsService(db)
    return await service.create(data)


@router.put("/{player_id}/{mode}", response_model=PlayerStatsResponse)
async def update_stats(player_id: uuid.UUID, mode: GameMode, data: PlayerStatsUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerStatsService(db)
    return await service.update(player_id, mode, data)


@router.delete("/{player_id}/{mode}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stats(player_id: uuid.UUID, mode: GameMode, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerStatsService(db)
    await service.delete(player_id, mode)
