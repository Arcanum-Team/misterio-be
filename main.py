from enum import Enum
from uuid import UUID
from partida import entities
from pony.orm import *
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
    owner: int
    nickname: str
    playerName: str


app = FastAPI()


@app.put("/players/order")
def read_root(player: PlayerOrder):
    return player


@app.post("/games")
@db_session
def read_item(game: Game):
    g_id= entities.addGame(game.name)
    p_id= entities.addPlayer(game.playerName, game.nickname, game.name, True)
    g= entities.getGamebyName(game.name)
    g[0].players.add(entities.getPlayerbyID(p_id))
    return game


@app.get("/game/{gameName}")
@db_session
def read_game(gameName: str):
    res = {""}
    game = entities.getGamebyName(gameName)
    if(game):
        res =  {"id": game[0].id,"name": game[0].name,
                "cantPlayers": len(game[0].players)}
    return res

@app.get("/games")
@db_session
def read_games():
    games = entities.getGames()
    res = []
    for game in games:
        res.append({"id": game.id,"name": game.name,
            "cantPlayers": len(game.players)}) 
    return res

@app.put("/games/start/{gameName}/{host_id}")
@db_session
def startGame(gameName:str, host_id:int):
    entities.startGame(gameName,host_id)
    return {"message: Partida empezada"}