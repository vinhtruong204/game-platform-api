from pydantic import BaseModel


class ModeCreate(BaseModel):
    name: str
    type: str
    code: str | None = None
    players_per_team: int = 1
    selection_weight: int = 0


class ModeUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    code: str | None = None
    players_per_team: int | None = None
    selection_weight: int | None = None


class ModeResponse(BaseModel):
    mode_id: int
    name: str
    type: str
    code: str | None
    players_per_team: int
    selection_weight: int

    model_config = {"from_attributes": True}
