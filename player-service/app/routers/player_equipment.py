import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_equipment import SlotType
from app.models.player_session import PlayerSession
from app.schemas.player_equipment import PlayerEquipmentCreate, PlayerEquipmentUpdate, PlayerEquipmentResponse
from app.services.player_equipment_service import PlayerEquipmentService

router = APIRouter(prefix="/player-equipment", tags=["Player Equipment"])


@router.get("/", response_model=list[PlayerEquipmentResponse])
async def get_all_equipment(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerEquipmentService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/{slot_type}", response_model=PlayerEquipmentResponse)
async def get_equipment(player_id: uuid.UUID, slot_type: SlotType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerEquipmentService(db)
    return await service.get_by_id(player_id, slot_type)


@router.post("/", response_model=PlayerEquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(data: PlayerEquipmentCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerEquipmentService(db)
    return await service.create(data)


@router.put("/{player_id}/{slot_type}", response_model=PlayerEquipmentResponse)
async def update_equipment(player_id: uuid.UUID, slot_type: SlotType, data: PlayerEquipmentUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerEquipmentService(db)
    return await service.update(player_id, slot_type, data)


@router.delete("/{player_id}/{slot_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(player_id: uuid.UUID, slot_type: SlotType, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerEquipmentService(db)
    await service.delete(player_id, slot_type)
