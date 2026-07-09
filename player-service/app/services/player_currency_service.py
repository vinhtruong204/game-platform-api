import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_currency import PlayerCurrency, CurrencyType
from app.repositories.player_currency_repository import PlayerCurrencyRepository
from app.schemas.player_currency import PlayerCurrencyCreate, PlayerCurrencyUpdate


class PlayerCurrencyService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerCurrencyRepository(db)

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerCurrency]:
        return await self.repo.get_all(player_id=player_id)

    async def get_by_id(self, player_id: uuid.UUID, currency_type: CurrencyType) -> PlayerCurrency:
        currency = await self.repo.get_by_id(player_id, currency_type)
        if not currency:
            raise HTTPException(status_code=404, detail="Player currency not found")
        return currency

    async def create(self, data: PlayerCurrencyCreate) -> PlayerCurrency:
        currency = PlayerCurrency(**data.model_dump())
        return await self.repo.create(currency)

    async def update(self, player_id: uuid.UUID, currency_type: CurrencyType, data: PlayerCurrencyUpdate) -> PlayerCurrency:
        currency = await self.get_by_id(player_id, currency_type)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(currency, update_data)

    async def add_currency(self, player_id: uuid.UUID, currency_type: CurrencyType, amount: int) -> PlayerCurrency:
        currency = await self.get_by_id(player_id, currency_type)
        new_amount = currency.amount + amount
        return await self.repo.update(currency, {"amount": new_amount})

    async def deduct_currency(self, player_id: uuid.UUID, currency_type: CurrencyType, amount: int) -> PlayerCurrency:
        currency = await self.get_by_id(player_id, currency_type)
        if currency.amount < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        new_amount = currency.amount - amount
        return await self.repo.update(currency, {"amount": new_amount})

    async def delete(self, player_id: uuid.UUID, currency_type: CurrencyType) -> None:
        currency = await self.get_by_id(player_id, currency_type)
        await self.repo.delete(currency)
