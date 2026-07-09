import uuid
from datetime import datetime

import jwt
from fastapi import HTTPException

from app.core.config import settings


def create_session_token(session_id: str, player_id: uuid.UUID, expires_at: datetime) -> str:
    payload = {
        "session_id": session_id,
        "player_id": str(player_id),
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_session_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")
