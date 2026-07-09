import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.models.shop import ItemType, CurrencyType
from app.schemas.shop import ShopCreate, ShopUpdate, ShopResponse
from app.services.shop_service import ShopService

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.get("/", response_model=list[ShopResponse])
async def get_all_shops(
    item_type: ItemType | None = None,
    currency_type: CurrencyType | None = None,
    is_today: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _player_id: uuid.UUID = Depends(get_current_player_id),
):
    service = ShopService(db)
    return await service.get_all(
        item_type=item_type,
        currency_type=currency_type,
        is_today=is_today,
        skip=skip,
        limit=limit,
    )


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop(shop_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ShopService(db)
    return await service.get_by_id(shop_id)


@router.post("/", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
async def create_shop(data: ShopCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ShopService(db)
    return await service.create(data)


@router.put("/{shop_id}", response_model=ShopResponse)
async def update_shop(shop_id: int, data: ShopUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ShopService(db)
    return await service.update(shop_id, data)


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(shop_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = ShopService(db)
    await service.delete(shop_id)
