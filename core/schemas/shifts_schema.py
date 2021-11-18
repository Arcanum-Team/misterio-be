from uuid import UUID
from core.exceptions import MysteryException
from pydantic import BaseModel, Field, validator


class Movement(BaseModel):
    game_id: UUID
    player_id: UUID
    next_box_id: int = Field(ge=1, le=80)
    dice_value: int = Field(ge=1, le=6)

class Acusse(BaseModel):
    game_id: UUID
    player_id: UUID
    monster_id: int
    victim_id: int
    enclosure_id: int


class RollDice(BaseModel):
    game_id: UUID
    player_id: UUID
    dice: int

    @validator('dice')
    def dice_range(cls, d):
        if d not in range(7):
            raise MysteryException(message="Dice not in correct range", status_code=400)


class SuspectResponse(BaseModel):
    game_id: UUID
    player_id: UUID
    card: int