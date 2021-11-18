from pydantic import Field

from core.schemas import BasicGameInput


class Movement(BasicGameInput):
    next_box_id: int = Field(ge=1, le=80)
    dice_value: int = Field(ge=1, le=6)


class Acusse(BasicGameInput):
    monster_id: int
    victim_id: int
    enclosure_id: int


class RollDice(BasicGameInput):
    dice: int = Field(ge=1, le=6)
