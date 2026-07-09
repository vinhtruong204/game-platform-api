from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_session_token
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.repositories.player_session_repository import PlayerSessionRepository

bearer_scheme = HTTPBearer()


async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> PlayerSession:
    token = credentials.credentials
    payload = decode_session_token(token)

    repo = PlayerSessionRepository(db)
    session = await repo.get_by_id(payload["session_id"])

    if not session or session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Session is invalid or revoked")

    return session
