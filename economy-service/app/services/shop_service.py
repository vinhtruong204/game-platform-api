from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shop import Shop, ItemType, CurrencyType
from app.repositories.shop_repository import ShopRepository
from app.schemas.shop import ShopCreate, ShopUpdate


class ShopService:
    def __init__(self, db: AsyncSession):
        self.repo = ShopRepository(db)

    async def get_all(
        self,
        item_type: ItemType | None = None,
        currency_type: CurrencyType | None = None,
        is_today: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Shop]:
        return await self.repo.get_all(
            item_type=item_type,
            currency_type=currency_type,
            is_today=is_today,
            skip=skip,
            limit=limit,
        )

    async def get_by_id(self, shop_id: int) -> Shop:
        shop = await self.repo.get_by_id(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop item not found")
        return shop

    async def create(self, data: ShopCreate) -> Shop:
        shop = Shop(**data.model_dump())
        return await self.repo.create(shop)

    async def update(self, shop_id: int, data: ShopUpdate) -> Shop:
        shop = await self.get_by_id(shop_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(shop, update_data)

    async def delete(self, shop_id: int) -> None:
        shop = await self.get_by_id(shop_id)
        await self.repo.delete(shop)
