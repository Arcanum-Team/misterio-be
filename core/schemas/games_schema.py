from pydantic.main import BaseModel


class GameJoin(BaseModel):
    name: str
    user: str
    nickname: str


class Game(BaseModel):
    name: str
    nickname: str
    playerName: str
