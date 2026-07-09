import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.match_history import MatchHistoryCreate, MatchHistoryUpdate, MatchHistoryResponse
from app.services.match_history_service import MatchHistoryService

router = APIRouter(prefix="/matches", tags=["Match History"])


@router.get("/", response_model=list[MatchHistoryResponse])
async def get_all_matches(db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchHistoryService(db)
    return await service.get_all()


@router.get("/{match_id}", response_model=MatchHistoryResponse)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchHistoryService(db)
    return await service.get_by_id(match_id)


@router.post("/", response_model=MatchHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_match(data: MatchHistoryCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchHistoryService(db)
    return await service.create(data)


@router.put("/{match_id}", response_model=MatchHistoryResponse)
async def update_match(match_id: int, data: MatchHistoryUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchHistoryService(db)
    return await service.update(match_id, data)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MatchHistoryService(db)
    await service.delete(match_id)
