from pydantic import BaseModel


class WeaponCreate(BaseModel):
    name: str
    weapon_type: str
    damage: int
    fire_rate: float
    image: str
    ammo: int = 0


class WeaponUpdate(BaseModel):
    name: str | None = None
    weapon_type: str | None = None
    damage: int | None = None
    fire_rate: float | None = None
    image: str | None = None
    ammo: int | None = None


class WeaponResponse(BaseModel):
    weapon_id: int
    name: str
    weapon_type: str
    damage: int
    fire_rate: float
    image: str
    ammo: int

    model_config = {"from_attributes": True}
