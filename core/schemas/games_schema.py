from typing import Optional, List
from uuid import UUID

from pydantic import validator, Required, Field
from pydantic.main import BaseModel


class GameJoin(BaseModel):
    game_id: UUID
    nickname: str = Field(min_length=1, max_length=20)


class NewGame(BaseModel):
    game_name: Optional[str] = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)


class PlayerInDB(BaseModel):
    nickname: str
    is_host: bool
    order: Optional[int]

    class Config:
        orm_mode = True


class GameBasicInfo(BaseModel):
    name: str
    player_count: int
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
