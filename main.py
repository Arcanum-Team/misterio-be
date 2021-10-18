from enum import Enum
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
    player_id: int
    order: Position


class Game(BaseModel):
    name: str
    owner: int


app = FastAPI()


@app.put("/players/order")
def read_root(player: PlayerOrder):
    return player


@app.post("/game")
def read_item(game: Game):
    return game
