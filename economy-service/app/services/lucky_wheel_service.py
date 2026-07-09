from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lucky_wheel_item import LuckyWheelItem
from app.models.shop import CurrencyType
from app.repositories.lucky_wheel_repository import LuckyWheelRepository
from app.schemas.lucky_wheel import LuckyWheelItemCreate, LuckyWheelItemUpdate


class LuckyWheelService:
    def __init__(self, db: AsyncSession):
        self.repo = LuckyWheelRepository(db)

    async def get_all(self) -> list[LuckyWheelItem]:
        return await self.repo.get_all()

    async def get_by_wheel_type(self, wheel_type: CurrencyType) -> list[LuckyWheelItem]:
        return await self.repo.get_by_wheel_type(wheel_type)

    async def get_by_id(self, item_id: int) -> LuckyWheelItem:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Lucky wheel item not found")
        return item

    async def create(self, data: LuckyWheelItemCreate) -> LuckyWheelItem:
        item = LuckyWheelItem(**data.model_dump())
        return await self.repo.create(item)

    async def update(self, item_id: int, data: LuckyWheelItemUpdate) -> LuckyWheelItem:
        item = await self.get_by_id(item_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(item, update_data)

    async def delete(self, item_id: int) -> None:
        item = await self.get_by_id(item_id)
        await self.repo.delete(item)
