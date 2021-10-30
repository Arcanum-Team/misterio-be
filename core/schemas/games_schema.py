from typing import Optional, List
from uuid import UUID

from pydantic import validator, Field
from pydantic.main import BaseModel


class GameJoin(BaseModel):
    game_name: str = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)


class GameStart(BaseModel):
    game_id: UUID
    player_id: UUID


class NewGame(BaseModel):
    game_name: Optional[str] = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)


class PlayerInDB(BaseModel):
    id: Optional[UUID]
    nickname: str
    host: bool
    order: Optional[int]

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
    players: List[PlayerInDB]

    @validator('players', pre=True, allow_reuse=True)
    def players_to_players_in_db(cls, values):
        return [v for v in values]

    class Config:
        orm_mode = True
