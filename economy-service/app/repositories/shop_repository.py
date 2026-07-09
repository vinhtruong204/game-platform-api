from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shop import Shop, ItemType, CurrencyType


class ShopRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        item_type: ItemType | None = None,
        currency_type: CurrencyType | None = None,
        is_today: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Shop]:
        stmt = select(Shop)
        if item_type is not None:
            stmt = stmt.where(Shop.item_type == item_type)
        if currency_type is not None:
            stmt = stmt.where(Shop.currency_type == currency_type)
        if is_today is not None:
            stmt = stmt.where(Shop.is_today == is_today)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, shop_id: int) -> Shop | None:
        result = await self.db.execute(
            select(Shop).where(Shop.shop_id == shop_id)
        )
        return result.scalar_one_or_none()

    async def create(self, shop: Shop) -> Shop:
        self.db.add(shop)
        await self.db.flush()
        await self.db.refresh(shop)
        return shop

    async def update(self, shop: Shop, data: dict) -> Shop:
        for key, value in data.items():
            setattr(shop, key, value)
        await self.db.flush()
        await self.db.refresh(shop)
        return shop

    async def delete(self, shop: Shop) -> None:
        await self.db.delete(shop)
        await self.db.flush()
