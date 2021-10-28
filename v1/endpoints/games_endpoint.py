from fastapi import APIRouter
from pony.orm import db_session

from core.models.games_repository import add_player, get_game_by_name, add_game, get_games
from core.models.player_repository import get_player_by_id
from core.schemas import games_schema
from core.schemas.games_schema import Game

games_router = APIRouter()


@games_router.post("/join")
@db_session
def read_game_join(game_join: games_schema.GameJoin):
    p_id = add_player(game_join.user, game_join.nickname, game_join.name, False)
    game = get_game_by_name(game_join.name)
    player = get_player_by_id(p_id)
    if game:
        game[0].players.add(player[0])
    return game_join


@games_router.post("/")
@db_session
def create_game(game: Game):
    game_saved = add_game(game.name)
    p_id = add_player(game.playerName, game.nickname, game.name, True)
    g = get_game_by_name(game.name)
    g[0].players.add(get_player_by_id(p_id))
    return game_saved


@games_router.get("/{gameName}")
@db_session
def read_game(game_name: str):
    return get_game_by_name(game_name)


@games_router.get("/")
@db_session
def read_games():
    return get_games()


@games_router.put("/start/{gameName}/{host_id}")
@db_session
def start_game(game_name: str, host_id: int):
    start_game(game_name, host_id)
