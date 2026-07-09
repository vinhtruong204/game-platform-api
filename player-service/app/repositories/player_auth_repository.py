from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_auth import PlayerAuth
from app.models.enums import AuthProvider


class PlayerAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_provider_uid(self, provider: AuthProvider, provider_uid: str) -> PlayerAuth | None:
        result = await self.db.execute(
            select(PlayerAuth).where(
                PlayerAuth.provider == provider,
                PlayerAuth.provider_uid == provider_uid,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, auth: PlayerAuth) -> PlayerAuth:
        self.db.add(auth)
        await self.db.flush()
        await self.db.refresh(auth)
        return auth

    async def update_last_login(self, auth: PlayerAuth) -> PlayerAuth:
        auth.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(auth)
        return auth
