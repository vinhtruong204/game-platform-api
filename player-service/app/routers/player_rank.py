import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.player_rank import PlayerRankCreate, PlayerRankUpdate, PlayerRankResponse
from app.services.player_rank_service import PlayerRankService

router = APIRouter(prefix="/player-ranks", tags=["Player Ranks"])


@router.get("/", response_model=list[PlayerRankResponse])
async def get_all_player_ranks(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerRankService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/{season_id}", response_model=PlayerRankResponse)
async def get_player_rank(player_id: uuid.UUID, season_id: int, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerRankService(db)
    return await service.get_by_id(player_id, season_id)


@router.post("/", response_model=PlayerRankResponse, status_code=status.HTTP_201_CREATED)
async def create_player_rank(data: PlayerRankCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerRankService(db)
    return await service.create(data)


@router.put("/{player_id}/{season_id}", response_model=PlayerRankResponse)
async def update_player_rank(player_id: uuid.UUID, season_id: int, data: PlayerRankUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerRankService(db)
    return await service.update(player_id, season_id, data)


@router.delete("/{player_id}/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player_rank(player_id: uuid.UUID, season_id: int, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerRankService(db)
    await service.delete(player_id, season_id)
