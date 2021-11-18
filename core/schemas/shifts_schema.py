from uuid import UUID
from pydantic import BaseModel, Field

from core.schemas import PlayerGame


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
    dice: int = Field(ge=1, le=6)
