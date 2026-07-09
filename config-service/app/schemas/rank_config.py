from pydantic import BaseModel


class RankConfigCreate(BaseModel):
    name: str
    min_point: int
    max_point: int
    image: str


class RankConfigUpdate(BaseModel):
    name: str | None = None
    min_point: int | None = None
    max_point: int | None = None
    image: str | None = None


class RankConfigResponse(BaseModel):
    rank_id: int
    name: str
    min_point: int
    max_point: int
    image: str

    model_config = {"from_attributes": True}
