import uuid

from pydantic import BaseModel, Field

from app.models.player_currency import CurrencyType


class PlayerCurrencyCreate(BaseModel):
    player_id: uuid.UUID
    currency_type: CurrencyType
    amount: int = 0


class PlayerCurrencyUpdate(BaseModel):
    amount: int


class CurrencyModify(BaseModel):
    amount: int = Field(..., gt=0)


class PlayerCurrencyResponse(BaseModel):
    player_id: uuid.UUID
    currency_type: CurrencyType
    amount: int

    model_config = {"from_attributes": True}
