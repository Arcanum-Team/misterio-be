from enum import Enum
from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel


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


class Game(BaseModel):
    name: str
    owner: UUID

class Game_join(BaseModel): #
    name: str
    user: UUID


app = FastAPI()


@app.put("/players/order")
def read_root(player: PlayerOrder):
    return player


@app.post("/games")
def read_item(game: Game):
    return game


@app.post("/games/join")
def read_join(game: Game_join):
    return game