from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    GoogleSignInRequest,
    AuthResponse,
    SignOutRequest,
    RefreshRequest,
    RefreshResponse,
    DevLoginRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def google_sign_in(data: GoogleSignInRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.google_sign_in(data.id_token, data.device_info)


@router.post("/dev-login", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def dev_login(data: DevLoginRequest, db: AsyncSession = Depends(get_db)):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=403, detail="Dev login is disabled")
    service = AuthService(db)
    return await service.dev_login(data.name, data.device_info)


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(data: SignOutRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.sign_out(data.session_token)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(data.session_token)
