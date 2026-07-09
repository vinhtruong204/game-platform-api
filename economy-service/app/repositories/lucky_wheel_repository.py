from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lucky_wheel_item import LuckyWheelItem
from app.models.shop import CurrencyType


class LuckyWheelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[LuckyWheelItem]:
        result = await self.db.execute(
            select(LuckyWheelItem).order_by(LuckyWheelItem.wheel_type, LuckyWheelItem.slot_index)
        )
        return list(result.scalars().all())

    async def get_by_wheel_type(self, wheel_type: CurrencyType) -> list[LuckyWheelItem]:
        result = await self.db.execute(
            select(LuckyWheelItem)
            .where(LuckyWheelItem.wheel_type == wheel_type)
            .order_by(LuckyWheelItem.slot_index)
        )
        return list(result.scalars().all())

    async def get_by_id(self, item_id: int) -> LuckyWheelItem | None:
        result = await self.db.execute(
            select(LuckyWheelItem).where(LuckyWheelItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(self, item: LuckyWheelItem) -> LuckyWheelItem:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(self, item: LuckyWheelItem, data: dict) -> LuckyWheelItem:
        for key, value in data.items():
            setattr(item, key, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item: LuckyWheelItem) -> None:
        await self.db.delete(item)
        await self.db.flush()
