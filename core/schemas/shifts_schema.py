from uuid import UUID

from pydantic import BaseModel


class Movement(BaseModel):
    game_id: UUID
    player_id: UUID
    box_id: int
