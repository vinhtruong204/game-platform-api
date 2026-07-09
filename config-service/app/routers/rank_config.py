import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.rank_config import RankConfigCreate, RankConfigUpdate, RankConfigResponse
from app.services.rank_config_service import RankConfigService

router = APIRouter(prefix="/rank-configs", tags=["Rank Configs"])


@router.get("/", response_model=list[RankConfigResponse])
async def get_all_rank_configs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = RankConfigService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{rank_id}", response_model=RankConfigResponse)
async def get_rank_config(rank_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = RankConfigService(db)
    return await service.get_by_id(rank_id)


@router.post("/", response_model=RankConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_rank_config(data: RankConfigCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = RankConfigService(db)
    return await service.create(data)


@router.put("/{rank_id}", response_model=RankConfigResponse)
async def update_rank_config(rank_id: int, data: RankConfigUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = RankConfigService(db)
    return await service.update(rank_id, data)


@router.delete("/{rank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rank_config(rank_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = RankConfigService(db)
    await service.delete(rank_id)
