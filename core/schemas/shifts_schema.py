from uuid import UUID

from pydantic import Field, BaseModel

from core.schemas.games_schema import BasicGameInput


class Movement(BasicGameInput):
    next_box_id: int = Field(ge=1, le=80)
    dice_value: int = Field(ge=1, le=6)


class Acusse(BasicGameInput):
    monster_id: int
    victim_id: int
    enclosure_id: int


class Suspect(BasicGameInput):
    monster_id: int
    victim_id: int


class RollDice(BaseModel):
    game_id: UUID
    player_id: UUID
    dice: int = Field(ge=1, le=6)


class SuspectResponse(BaseModel):
    game_id: UUID
    from_player: UUID
    to_player: UUID
    card: int
