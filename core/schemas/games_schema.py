from typing import Optional, List
from uuid import UUID

from pydantic import validator, Field
from pydantic.main import BaseModel

from core.schemas.player_schema import PlayerOutput


class GameJoin(BaseModel):
    game_name: str = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)


class GameStart(BaseModel):
    game_id: UUID
    player_id: UUID


class GamePassTurn(BaseModel):
    game_id: UUID


class NewGame(BaseModel):
    game_name: Optional[str] = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)


class SimpleBox(BaseModel):
    id: int

    class Config:
        orm_mode = True


class GameBasicInfo(BaseModel):
    name: str
    player_count: Optional[int]
    started: bool

    class Config:
        orm_mode = True


class GameOutput(GameBasicInfo):
    id: UUID
    turn: Optional[int]

    class Config:
        orm_mode = True


class GameListPlayers(BaseModel):
    game: GameOutput
    players: List[PlayerOutput]


class GamePlayer(BaseModel):
    game: GameOutput
    player: PlayerOutput
