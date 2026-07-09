import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.player_achievement import PlayerAchievementCreate, PlayerAchievementUpdate, PlayerAchievementResponse
from app.services.player_achievement_service import PlayerAchievementService

router = APIRouter(prefix="/player-achievements", tags=["Player Achievements"])


@router.get("/", response_model=list[PlayerAchievementResponse])
async def get_all_achievements(player_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerAchievementService(db)
    return await service.get_all(player_id=player_id)


@router.get("/{player_id}/{achievement_id}", response_model=PlayerAchievementResponse)
async def get_achievement(player_id: uuid.UUID, achievement_id: int, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerAchievementService(db)
    return await service.get_by_id(player_id, achievement_id)


@router.post("/", response_model=PlayerAchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(data: PlayerAchievementCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerAchievementService(db)
    return await service.create(data)


@router.put("/{player_id}/{achievement_id}", response_model=PlayerAchievementResponse)
async def update_achievement(player_id: uuid.UUID, achievement_id: int, data: PlayerAchievementUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerAchievementService(db)
    return await service.update(player_id, achievement_id, data)


@router.delete("/{player_id}/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(player_id: uuid.UUID, achievement_id: int, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerAchievementService(db)
    await service.delete(player_id, achievement_id)
