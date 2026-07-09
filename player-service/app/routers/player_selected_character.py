import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_player
from app.db.session import get_db
from app.models.player_session import PlayerSession
from app.schemas.player_selected_character import (
    PlayerSelectedCharacterCreate,
    PlayerSelectedCharacterUpdate,
    PlayerSelectedCharacterResponse,
)
from app.services.player_selected_character_service import PlayerSelectedCharacterService

router = APIRouter(prefix="/player-selected-characters", tags=["Player Selected Characters"])


@router.get("/", response_model=list[PlayerSelectedCharacterResponse])
async def get_all_selected_characters(db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerSelectedCharacterService(db)
    return await service.get_all()


@router.get("/{player_id}", response_model=PlayerSelectedCharacterResponse)
async def get_selected_character(player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerSelectedCharacterService(db)
    return await service.get_by_id(player_id)


@router.post("/", response_model=PlayerSelectedCharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_selected_character(data: PlayerSelectedCharacterCreate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerSelectedCharacterService(db)
    return await service.create(data)


@router.put("/{player_id}", response_model=PlayerSelectedCharacterResponse)
async def update_selected_character(player_id: uuid.UUID, data: PlayerSelectedCharacterUpdate, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerSelectedCharacterService(db)
    return await service.update(player_id, data)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_selected_character(player_id: uuid.UUID, db: AsyncSession = Depends(get_db), _session: PlayerSession = Depends(get_current_player)):
    service = PlayerSelectedCharacterService(db)
    await service.delete(player_id)
