import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_session_token, decode_session_token
from app.models.enums import AuthProvider
from app.models.player_auth import PlayerAuth
from app.models.player_profile import PlayerProfile
from app.models.player_session import PlayerSession
from app.repositories.player_auth_repository import PlayerAuthRepository
from app.repositories.player_session_repository import PlayerSessionRepository
from app.repositories.player_profile_repository import PlayerProfileRepository
from app.services.google_auth import verify_google_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repo = PlayerAuthRepository(db)
        self.session_repo = PlayerSessionRepository(db)
        self.profile_repo = PlayerProfileRepository(db)

    async def google_sign_in(self, id_token: str, device_info: str | None = None) -> dict:
        google_info = await verify_google_token(id_token)

        auth = await self.auth_repo.get_by_provider_uid(AuthProvider.google, google_info["sub"])
        is_new_player = False

        if auth is None:
            # Create new player profile
            player = PlayerProfile(
                name=google_info.get("name") or "Player",
                is_new_player=True,
            )
            player = await self.profile_repo.create(player)

            # Create auth record
            auth = PlayerAuth(
                player_id=player.player_id,
                provider=AuthProvider.google,
                provider_uid=google_info["sub"],
                email=google_info.get("email"),
                display_name=google_info.get("name"),
                avatar_url=google_info.get("picture"),
                id_token_hash=hashlib.sha256(id_token.encode()).hexdigest(),
            )
            auth = await self.auth_repo.create(auth)
            is_new_player = True
        else:
            await self.auth_repo.update_last_login(auth)
            player = await self.profile_repo.get_by_id(auth.player_id)
            is_new_player = player.is_new_player if player else False

        # Create session
        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRATION_DAYS)

        session = PlayerSession(
            session_id=session_id,
            player_id=auth.player_id,
            auth_id=auth.auth_id,
            device_info=device_info,
            expires_at=expires_at,
        )
        await self.session_repo.create(session)

        session_token = create_session_token(session_id, auth.player_id, expires_at)

        return {
            "session_token": session_token,
            "player_id": auth.player_id,
            "is_new_player": is_new_player,
        }

    async def dev_login(self, name: str = "DevPlayer", device_info: str | None = None) -> dict:
        provider_uid = f"dev-{name}"
        auth = await self.auth_repo.get_by_provider_uid(AuthProvider.dev, provider_uid)
        is_new_player = False

        if auth is None:
            player = PlayerProfile(
                name=name,
                is_new_player=True,
            )
            player = await self.profile_repo.create(player)

            auth = PlayerAuth(
                player_id=player.player_id,
                provider=AuthProvider.dev,
                provider_uid=provider_uid,
            )
            auth = await self.auth_repo.create(auth)
            is_new_player = True
        else:
            await self.auth_repo.update_last_login(auth)
            player = await self.profile_repo.get_by_id(auth.player_id)
            is_new_player = player.is_new_player if player else False

        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRATION_DAYS)

        session = PlayerSession(
            session_id=session_id,
            player_id=auth.player_id,
            auth_id=auth.auth_id,
            device_info=device_info,
            expires_at=expires_at,
        )
        await self.session_repo.create(session)

        session_token = create_session_token(session_id, auth.player_id, expires_at)

        return {
            "session_token": session_token,
            "player_id": auth.player_id,
            "is_new_player": is_new_player,
        }

    async def sign_out(self, session_token: str) -> None:
        payload = decode_session_token(session_token)
        session = await self.session_repo.get_by_id(payload["session_id"])

        if not session or session.revoked_at is not None:
            raise HTTPException(status_code=404, detail="Session not found or already revoked")

        await self.session_repo.revoke(session)

    async def refresh(self, session_token: str) -> dict:
        payload = decode_session_token(session_token)
        session = await self.session_repo.get_by_id(payload["session_id"])

        if not session or session.revoked_at is not None:
            raise HTTPException(status_code=401, detail="Session is invalid or revoked")

        if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session has expired")

        # Create new session
        new_session_id = str(uuid.uuid4())
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRATION_DAYS)

        new_session = PlayerSession(
            session_id=new_session_id,
            player_id=session.player_id,
            auth_id=session.auth_id,
            device_info=session.device_info,
            expires_at=new_expires_at,
        )
        await self.session_repo.create(new_session)

        # Revoke old session
        await self.session_repo.revoke(session)

        new_token = create_session_token(new_session_id, session.player_id, new_expires_at)

        return {
            "session_token": new_token,
            "expires_at": new_expires_at,
        }
