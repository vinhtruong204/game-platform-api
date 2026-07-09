from pydantic import BaseModel


class MapCreate(BaseModel):
    name: str
    image: str


class MapUpdate(BaseModel):
    name: str | None = None
    image: str | None = None


class MapResponse(BaseModel):
    map_id: int
    name: str
    image: str

    model_config = {"from_attributes": True}
