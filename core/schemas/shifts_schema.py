from uuid import UUID

from pydantic import BaseModel, Field


class Movement(BaseModel):
    game_id: UUID
    player_id: UUID
    next_box_id: int = Field(ge=0, le=79)
    dice_value: int = Field(ge=1, le=6)
