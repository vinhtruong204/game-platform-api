from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weapon import Weapon
from app.repositories.weapon_repository import WeaponRepository
from app.schemas.weapon import WeaponCreate, WeaponUpdate


class WeaponService:
    def __init__(self, db: AsyncSession):
        self.repo = WeaponRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Weapon]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, weapon_id: int) -> Weapon:
        weapon = await self.repo.get_by_id(weapon_id)
        if not weapon:
            raise HTTPException(status_code=404, detail="Weapon not found")
        return weapon

    async def create(self, data: WeaponCreate) -> Weapon:
        weapon = Weapon(**data.model_dump())
        return await self.repo.create(weapon)

    async def update(self, weapon_id: int, data: WeaponUpdate) -> Weapon:
        weapon = await self.get_by_id(weapon_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(weapon, update_data)

    async def delete(self, weapon_id: int) -> None:
        weapon = await self.get_by_id(weapon_id)
        await self.repo.delete(weapon)
