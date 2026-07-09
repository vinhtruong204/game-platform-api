import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_equipment import PlayerEquipment, SlotType
from app.repositories.player_equipment_repository import PlayerEquipmentRepository
from app.schemas.player_equipment import PlayerEquipmentCreate, PlayerEquipmentUpdate


class PlayerEquipmentService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerEquipmentRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerEquipment]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, slot_type: SlotType) -> PlayerEquipment:
        equipment = await self.repo.get_by_id(player_id, slot_type)
        if not equipment:
            raise HTTPException(status_code=404, detail="Player equipment not found")
        return equipment

    async def create(self, data: PlayerEquipmentCreate) -> PlayerEquipment:
        equipment = PlayerEquipment(**data.model_dump())
        return await self.repo.create(equipment)

    async def update(self, player_id: uuid.UUID, slot_type: SlotType, data: PlayerEquipmentUpdate) -> PlayerEquipment:
        equipment = await self.repo.get_by_id(player_id, slot_type)
        if not equipment:
            equipment = PlayerEquipment(player_id=player_id, slot_type=slot_type, **data.model_dump())
            return await self.repo.create(equipment)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(equipment, update_data)

    async def delete(self, player_id: uuid.UUID, slot_type: SlotType) -> None:
        equipment = await self.get_by_id(player_id, slot_type)
        await self.repo.delete(equipment)
