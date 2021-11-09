from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic.main import BaseModel


class Position(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


class PlayerOrder(BaseModel):
    player_id: UUID
    game_id: UUID
    order: Position


class GameInDB(BaseModel):
    id: UUID
    name: str
    started: bool

    class Config:
        orm_mode = True


class BoxOutput(BaseModel):
    id: int
    attribute: str


class PlayerOutput(BaseModel):
    id: UUID
    nickname: str
    host: bool
    game: GameInDB
    current_position: Optional[BoxOutput]

    class Config:
        orm_mode = True


class BasicPlayerInfo(BaseModel):
    id: UUID
    nickname: str
