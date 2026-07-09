import uuid
from datetime import datetime

from pydantic import BaseModel


class GoogleSignInRequest(BaseModel):
    id_token: str
    device_info: str | None = None


class AuthResponse(BaseModel):
    session_token: str
    player_id: uuid.UUID
    is_new_player: bool


class SignOutRequest(BaseModel):
    session_token: str


class RefreshRequest(BaseModel):
    session_token: str


class RefreshResponse(BaseModel):
    session_token: str
    expires_at: datetime


class DevLoginRequest(BaseModel):
    name: str = "DevPlayer"
    device_info: str | None = None
