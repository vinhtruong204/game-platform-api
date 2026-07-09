import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.mode import ModeCreate, ModeUpdate, ModeResponse
from app.services.mode_service import ModeService

router = APIRouter(prefix="/modes", tags=["Modes"])


@router.get("/", response_model=list[ModeResponse])
async def get_all_modes(db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ModeService(db)
    return await service.get_all()


@router.get("/{mode_id}", response_model=ModeResponse)
async def get_mode(mode_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ModeService(db)
    return await service.get_by_id(mode_id)


@router.post("/", response_model=ModeResponse, status_code=status.HTTP_201_CREATED)
async def create_mode(data: ModeCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ModeService(db)
    return await service.create(data)


@router.put("/{mode_id}", response_model=ModeResponse)
async def update_mode(mode_id: int, data: ModeUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ModeService(db)
    return await service.update(mode_id, data)


@router.delete("/{mode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mode(mode_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ModeService(db)
    await service.delete(mode_id)
