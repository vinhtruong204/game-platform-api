import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_inventory import ItemType
from app.models.player_session import PlayerSession
from app.schemas.player_inventory import PlayerInventoryCreate, PlayerInventoryUpdate, PlayerInventoryResponse
from app.services.player_inventory_service import PlayerInventoryService

router = APIRouter(prefix="/player-inventory", tags=["Player Inventory"])


@router.get("/", response_model=list[PlayerInventoryResponse])
async def get_all_inventory(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/type/{item_type}", response_model=list[PlayerInventoryResponse])
async def get_inventory_by_type(player_id: uuid.UUID, item_type: ItemType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    return await service.get_by_player_and_type(player_id, item_type)


@router.get("/{player_id}/{item_id}/{item_type}", response_model=PlayerInventoryResponse)
async def get_inventory_item(player_id: uuid.UUID, item_id: int, item_type: ItemType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    return await service.get_by_id(player_id, item_id, item_type)


@router.post("/", response_model=PlayerInventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(data: PlayerInventoryCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    return await service.create(data)


@router.put("/{player_id}/{item_id}/{item_type}", response_model=PlayerInventoryResponse)
async def update_inventory_item(player_id: uuid.UUID, item_id: int, item_type: ItemType, data: PlayerInventoryUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    return await service.update(player_id, item_id, item_type, data)


@router.delete("/{player_id}/{item_id}/{item_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(player_id: uuid.UUID, item_id: int, item_type: ItemType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerInventoryService(db)
    await service.delete(player_id, item_id, item_type)
