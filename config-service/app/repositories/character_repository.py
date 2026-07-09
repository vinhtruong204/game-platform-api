from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character


class CharacterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Character]:
        result = await self.db.execute(
            select(Character).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, character_id: int) -> Character | None:
        result = await self.db.execute(
            select(Character).where(Character.character_id == character_id)
        )
        return result.scalar_one_or_none()

    async def create(self, character: Character) -> Character:
        self.db.add(character)
        await self.db.flush()
        await self.db.refresh(character)
        return character

    async def update(self, character: Character, data: dict) -> Character:
        for key, value in data.items():
            setattr(character, key, value)
        await self.db.flush()
        await self.db.refresh(character)
        return character

    async def delete(self, character: Character) -> None:
        await self.db.delete(character)
        await self.db.flush()
