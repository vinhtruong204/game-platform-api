import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.models.shop import CurrencyType
from app.schemas.lucky_wheel import LuckyWheelItemCreate, LuckyWheelItemUpdate, LuckyWheelItemResponse
from app.services.lucky_wheel_service import LuckyWheelService

router = APIRouter(prefix="/lucky-wheel", tags=["Lucky Wheel"])


@router.get("/", response_model=list[LuckyWheelItemResponse])
async def get_wheel_items(
    wheel_type: CurrencyType | None = None,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = LuckyWheelService(db)
    if wheel_type is not None:
        return await service.get_by_wheel_type(wheel_type)
    return await service.get_all()


@router.get("/{item_id}", response_model=LuckyWheelItemResponse)
async def get_wheel_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = LuckyWheelService(db)
    return await service.get_by_id(item_id)


@router.post("/", response_model=LuckyWheelItemResponse, status_code=status.HTTP_201_CREATED)
async def create_wheel_item(
    data: LuckyWheelItemCreate,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = LuckyWheelService(db)
    return await service.create(data)


@router.put("/{item_id}", response_model=LuckyWheelItemResponse)
async def update_wheel_item(
    item_id: int,
    data: LuckyWheelItemUpdate,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = LuckyWheelService(db)
    return await service.update(item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wheel_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = LuckyWheelService(db)
    await service.delete(item_id)
