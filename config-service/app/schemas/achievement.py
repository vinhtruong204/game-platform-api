from pydantic import BaseModel


class AchievementCreate(BaseModel):
    name: str
    image: str
    requirement: str


class AchievementUpdate(BaseModel):
    name: str | None = None
    image: str | None = None
    requirement: str | None = None


class AchievementResponse(BaseModel):
    achievement_id: int
    name: str
    image: str
    requirement: str

    model_config = {"from_attributes": True}
