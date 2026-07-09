from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_session import PlayerSession


class PlayerSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: PlayerSession) -> PlayerSession:
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: str) -> PlayerSession | None:
        result = await self.db.execute(
            select(PlayerSession).where(PlayerSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def revoke(self, session: PlayerSession) -> PlayerSession:
        session.revoked_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(session)
        return session
