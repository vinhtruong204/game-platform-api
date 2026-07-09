import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player_id
from app.db.session import get_db
from app.schemas.achievement import AchievementCreate, AchievementUpdate, AchievementResponse
from app.services.achievement_service import AchievementService

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/", response_model=list[AchievementResponse])
async def get_all_achievements(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = AchievementService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{achievement_id}", response_model=AchievementResponse)
async def get_achievement(achievement_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = AchievementService(db)
    return await service.get_by_id(achievement_id)


@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(data: AchievementCreate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = AchievementService(db)
    return await service.create(data)


@router.put("/{achievement_id}", response_model=AchievementResponse)
async def update_achievement(achievement_id: int, data: AchievementUpdate, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = AchievementService(db)
    return await service.update(achievement_id, data)


@router.delete("/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(achievement_id: int, db: AsyncSession = Depends(get_db), _player_id: uuid.UUID = Depends(get_current_player_id)):
    service = AchievementService(db)
    await service.delete(achievement_id)
