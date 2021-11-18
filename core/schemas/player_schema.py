from typing import Optional, List
from uuid import UUID

from pydantic import Field
from pydantic.main import BaseModel

from core.schemas.games_schema import BasicGameInput, GameOutput


class PlayerBox(BasicGameInput):
    box_id: int = Field(ge=1, le=80)


class GameInDB(BaseModel):
    id: UUID
    name: str
    started: bool

    class Config:
        orm_mode = True


class BoxOutput(BaseModel):
    id: int
    attribute: str


class EnclosureOutput(BaseModel):
    id: int
    doors: Optional[List[BoxOutput]]


class PlayerOutput(BaseModel):
    id: UUID
    nickname: str
    order: Optional[int]
    host: bool
    current_position: Optional[BoxOutput]
    enclosure: Optional[EnclosureOutput]


class BasicPlayerInfo(BaseModel):
    id: UUID
    nickname: str


class PlayerPosition(BaseModel):
    current_position: Optional[int]
    enclosure: Optional[int]


class GameListPlayers(BaseModel):
    game: GameOutput
    players: List[PlayerOutput]


class GamePlayer(BaseModel):
    game: GameOutput
    player: PlayerOutput
