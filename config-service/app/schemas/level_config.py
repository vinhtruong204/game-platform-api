from pydantic import BaseModel


class LevelConfigCreate(BaseModel):
    min_exp: int
    max_exp: int
    reward_gold: int
    reward_diamond: int


class LevelConfigUpdate(BaseModel):
    min_exp: int | None = None
    max_exp: int | None = None
    reward_gold: int | None = None
    reward_diamond: int | None = None


class LevelConfigResponse(BaseModel):
    level_id: int
    min_exp: int
    max_exp: int
    reward_gold: int
    reward_diamond: int

    model_config = {"from_attributes": True}
