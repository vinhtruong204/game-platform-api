import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_currency import PlayerCurrency, CurrencyType


class PlayerCurrencyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, player_id: uuid.UUID | None = None) -> list[PlayerCurrency]:
        stmt = select(PlayerCurrency)
        if player_id is not None:
            stmt = stmt.where(PlayerCurrency.player_id == player_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, player_id: uuid.UUID, currency_type: CurrencyType) -> PlayerCurrency | None:
        result = await self.db.execute(
            select(PlayerCurrency).where(
                PlayerCurrency.player_id == player_id,
                PlayerCurrency.currency_type == currency_type,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, currency: PlayerCurrency) -> PlayerCurrency:
        self.db.add(currency)
        await self.db.flush()
        await self.db.refresh(currency)
        return currency

    async def update(self, currency: PlayerCurrency, data: dict) -> PlayerCurrency:
        for key, value in data.items():
            setattr(currency, key, value)
        await self.db.flush()
        await self.db.refresh(currency)
        return currency

    async def delete(self, currency: PlayerCurrency) -> None:
        await self.db.delete(currency)
        await self.db.flush()
