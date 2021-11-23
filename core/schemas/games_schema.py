from typing import Optional
from uuid import UUID

from pydantic import Field
from pydantic.main import BaseModel


class GameJoin(BaseModel):
    game_name: str = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)
    password: Optional[str] = Field(max_length=10)


class BasicGameInput(BaseModel):
    game_id: UUID
    player_id: UUID


class GamePassTurn(BaseModel):
    game_id: UUID


class NewGame(BaseModel):
    game_name: Optional[str] = Field(min_length=1, max_length=6)
    nickname: str = Field(min_length=1, max_length=20)
    password: Optional[str] = Field(max_length=10)


class SimpleBox(BaseModel):
    id: int

    class Config:
        orm_mode = True


class GameBasicInfo(BaseModel):
    name: str
    player_count: Optional[int]
    started: bool
    has_password: Optional[bool]

    class Config:
        orm_mode = True


class GameOutput(GameBasicInfo):
    id: UUID
    turn: Optional[int]

    class Config:
        orm_mode = True


class ChatMessage(BaseModel):
    game_id: UUID
    player_id: UUID
    message: str
