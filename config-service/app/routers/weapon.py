import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.weapon import WeaponCreate, WeaponUpdate, WeaponResponse
from app.services.weapon_service import WeaponService

router = APIRouter(prefix="/weapons", tags=["Weapons"])


@router.get("/", response_model=list[WeaponResponse])
async def get_all_weapons(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = WeaponService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{weapon_id}", response_model=WeaponResponse)
async def get_weapon(weapon_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = WeaponService(db)
    return await service.get_by_id(weapon_id)


@router.post("/", response_model=WeaponResponse, status_code=status.HTTP_201_CREATED)
async def create_weapon(data: WeaponCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = WeaponService(db)
    return await service.create(data)


@router.put("/{weapon_id}", response_model=WeaponResponse)
async def update_weapon(weapon_id: int, data: WeaponUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = WeaponService(db)
    return await service.update(weapon_id, data)


@router.delete("/{weapon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weapon(weapon_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = WeaponService(db)
    await service.delete(weapon_id)
