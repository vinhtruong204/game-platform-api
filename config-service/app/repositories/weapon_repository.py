from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weapon import Weapon


class WeaponRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Weapon]:
        result = await self.db.execute(
            select(Weapon).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, weapon_id: int) -> Weapon | None:
        result = await self.db.execute(
            select(Weapon).where(Weapon.weapon_id == weapon_id)
        )
        return result.scalar_one_or_none()

    async def create(self, weapon: Weapon) -> Weapon:
        self.db.add(weapon)
        await self.db.flush()
        await self.db.refresh(weapon)
        return weapon

    async def update(self, weapon: Weapon, data: dict) -> Weapon:
        for key, value in data.items():
            setattr(weapon, key, value)
        await self.db.flush()
        await self.db.refresh(weapon)
        return weapon

    async def delete(self, weapon: Weapon) -> None:
        await self.db.delete(weapon)
        await self.db.flush()
