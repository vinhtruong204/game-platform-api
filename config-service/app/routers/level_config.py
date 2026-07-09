import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.level_config import LevelConfigCreate, LevelConfigUpdate, LevelConfigResponse
from app.services.level_config_service import LevelConfigService

router = APIRouter(prefix="/level-configs", tags=["Level Configs"])


@router.get("/", response_model=list[LevelConfigResponse])
async def get_all_level_configs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = LevelConfigService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{level_id}", response_model=LevelConfigResponse)
async def get_level_config(level_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = LevelConfigService(db)
    return await service.get_by_id(level_id)


@router.post("/", response_model=LevelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_level_config(data: LevelConfigCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = LevelConfigService(db)
    return await service.create(data)


@router.put("/{level_id}", response_model=LevelConfigResponse)
async def update_level_config(level_id: int, data: LevelConfigUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = LevelConfigService(db)
    return await service.update(level_id, data)


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_level_config(level_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = LevelConfigService(db)
    await service.delete(level_id)
