from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_purchase_token import PlayerPurchaseToken


class PlayerPurchaseTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_token(self, purchase_token: str) -> PlayerPurchaseToken | None:
        result = await self.db.execute(
            select(PlayerPurchaseToken).where(
                PlayerPurchaseToken.purchase_token == purchase_token
            )
        )
        return result.scalar_one_or_none()

    async def create(self, token: PlayerPurchaseToken) -> PlayerPurchaseToken:
        self.db.add(token)
        await self.db.flush()
        await self.db.refresh(token)
        return token
