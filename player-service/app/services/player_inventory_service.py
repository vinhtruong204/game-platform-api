import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_inventory import PlayerInventory, ItemType
from app.repositories.player_inventory_repository import PlayerInventoryRepository
from app.schemas.player_inventory import PlayerInventoryCreate, PlayerInventoryUpdate


class PlayerInventoryService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerInventoryRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerInventory]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, item_id: int, item_type: ItemType) -> PlayerInventory:
        item = await self.repo.get_by_id(player_id, item_id, item_type)
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        return item

    async def get_by_player_and_type(self, player_id: uuid.UUID, item_type: ItemType) -> list[PlayerInventory]:
        return await self.repo.get_by_player_and_type(player_id, item_type)

    async def create(self, data: PlayerInventoryCreate) -> PlayerInventory:
        item = PlayerInventory(**data.model_dump())
        return await self.repo.create(item)

    async def update(self, player_id: uuid.UUID, item_id: int, item_type: ItemType, data: PlayerInventoryUpdate) -> PlayerInventory:
        item = await self.get_by_id(player_id, item_id, item_type)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(item, update_data)

    async def delete(self, player_id: uuid.UUID, item_id: int, item_type: ItemType) -> None:
        item = await self.get_by_id(player_id, item_id, item_type)
        await self.repo.delete(item)
