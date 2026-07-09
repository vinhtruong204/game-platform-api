import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_inventory import PlayerInventory, ItemType


class PlayerInventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerInventory]:
        stmt = select(PlayerInventory)
        if player_id is not None:
            stmt = stmt.where(PlayerInventory.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, item_id: int, item_type: ItemType) -> PlayerInventory | None:
        result = await self.db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.item_id == item_id,
                PlayerInventory.item_type == item_type,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_player_and_type(self, player_id: uuid.UUID, item_type: ItemType) -> list[PlayerInventory]:
        result = await self.db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player_id,
                PlayerInventory.item_type == item_type,
            )
        )
        return list(result.scalars().all())

    async def create(self, item: PlayerInventory) -> PlayerInventory:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(self, item: PlayerInventory, data: dict) -> PlayerInventory:
        for key, value in data.items():
            setattr(item, key, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item: PlayerInventory) -> None:
        await self.db.delete(item)
        await self.db.flush()
