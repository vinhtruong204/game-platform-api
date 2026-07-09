from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character
from app.repositories.character_repository import CharacterRepository
from app.schemas.character import CharacterCreate, CharacterUpdate


class CharacterService:
    def __init__(self, db: AsyncSession):
        self.repo = CharacterRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Character]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, character_id: int) -> Character:
        character = await self.repo.get_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        return character

    async def create(self, data: CharacterCreate) -> Character:
        character = Character(**data.model_dump())
        return await self.repo.create(character)

    async def update(self, character_id: int, data: CharacterUpdate) -> Character:
        character = await self.get_by_id(character_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(character, update_data)

    async def delete(self, character_id: int) -> None:
        character = await self.get_by_id(character_id)
        await self.repo.delete(character)
