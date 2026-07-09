import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_selected_character import PlayerSelectedCharacter
from app.repositories.player_selected_character_repository import PlayerSelectedCharacterRepository
from app.schemas.player_selected_character import PlayerSelectedCharacterCreate, PlayerSelectedCharacterUpdate


class PlayerSelectedCharacterService:
    def __init__(self, db: AsyncSession):
        self.repo = PlayerSelectedCharacterRepository(db)

    async def get_all(self) -> list[PlayerSelectedCharacter]:
        return await self.repo.get_all()

    async def get_by_id(self, player_id: uuid.UUID) -> PlayerSelectedCharacter:
        selected = await self.repo.get_by_id(player_id)
        if not selected:
            raise HTTPException(status_code=404, detail="Player selected character not found")
        return selected

    async def create(self, data: PlayerSelectedCharacterCreate) -> PlayerSelectedCharacter:
        selected = PlayerSelectedCharacter(**data.model_dump())
        try:
            return await self.repo.create(selected)
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Player already has a selected character")

    async def update(self, player_id: uuid.UUID, data: PlayerSelectedCharacterUpdate) -> PlayerSelectedCharacter:
        selected = await self.repo.get_by_id(player_id)
        if not selected:
            selected = PlayerSelectedCharacter(player_id=player_id, **data.model_dump())
            return await self.repo.create(selected)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(selected, update_data)

    async def delete(self, player_id: uuid.UUID) -> None:
        selected = await self.get_by_id(player_id)
        await self.repo.delete(selected)
