import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.match_player import MatchPlayerCreate, MatchPlayerUpdate, MatchPlayerResponse, WinningStreakResponse
from app.services.match_player_service import MatchPlayerService

router = APIRouter(prefix="/match-players", tags=["Match Players"])


@router.get("/", response_model=list[MatchPlayerResponse])
async def get_all_match_players(match_id: int | None = None, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchPlayerService(db)
    return await service.get_all(match_id=match_id)


@router.get("/{player_id}/winning-streak", response_model=WinningStreakResponse)
async def get_player_winning_streak(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = MatchPlayerService(db)
    streak = await service.get_winning_streak(player_id)
    return {"player_id": player_id, "winning_streak": streak}


@router.get("/{match_id}/{player_id}", response_model=MatchPlayerResponse)
async def get_match_player(match_id: int, player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchPlayerService(db)
    return await service.get_by_id(match_id, player_id)


@router.post("/", response_model=MatchPlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_match_player(data: MatchPlayerCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchPlayerService(db)
    return await service.create(data)


@router.put("/{match_id}/{player_id}", response_model=MatchPlayerResponse)
async def update_match_player(match_id: int, player_id: uuid.UUID, data: MatchPlayerUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchPlayerService(db)
    return await service.update(match_id, player_id, data)


@router.delete("/{match_id}/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match_player(match_id: int, player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchPlayerService(db)
    await service.delete(match_id, player_id)
