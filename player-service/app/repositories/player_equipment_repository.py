import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_equipment import PlayerEquipment, SlotType


class PlayerEquipmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerEquipment]:
        stmt = select(PlayerEquipment)
        if player_id is not None:
            stmt = stmt.where(PlayerEquipment.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, slot_type: SlotType) -> PlayerEquipment | None:
        result = await self.db.execute(
            select(PlayerEquipment).where(
                PlayerEquipment.player_id == player_id,
                PlayerEquipment.slot_type == slot_type,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, equipment: PlayerEquipment) -> PlayerEquipment:
        self.db.add(equipment)
        await self.db.flush()
        await self.db.refresh(equipment)
        return equipment

    async def update(self, equipment: PlayerEquipment, data: dict) -> PlayerEquipment:
        for key, value in data.items():
            setattr(equipment, key, value)
        await self.db.flush()
        await self.db.refresh(equipment)
        return equipment

    async def delete(self, equipment: PlayerEquipment) -> None:
        await self.db.delete(equipment)
        await self.db.flush()
