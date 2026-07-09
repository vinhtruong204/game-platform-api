import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.map import MapCreate, MapUpdate, MapResponse
from app.services.map_service import MapService

router = APIRouter(prefix="/maps", tags=["Maps"])


@router.get("/", response_model=list[MapResponse])
async def get_all_maps(db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MapService(db)
    return await service.get_all()


@router.get("/{map_id}", response_model=MapResponse)
async def get_map(map_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MapService(db)
    return await service.get_by_id(map_id)


@router.post("/", response_model=MapResponse, status_code=status.HTTP_201_CREATED)
async def create_map(data: MapCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MapService(db)
    return await service.create(data)


@router.put("/{map_id}", response_model=MapResponse)
async def update_map(map_id: int, data: MapUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MapService(db)
    return await service.update(map_id, data)


@router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_map(map_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = MapService(db)
    await service.delete(map_id)
