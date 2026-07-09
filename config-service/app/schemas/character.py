from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    character_type: str
    hp: int
    run_speed: float
    texture: str


class CharacterUpdate(BaseModel):
    name: str | None = None
    character_type: str | None = None
    hp: int | None = None
    run_speed: float | None = None
    texture: str | None = None


class CharacterResponse(BaseModel):
    character_id: int
    name: str
    character_type: str
    hp: int
    run_speed: float
    texture: str

    model_config = {"from_attributes": True}
