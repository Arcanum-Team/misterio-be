import logging
import random
import string

from fastapi import APIRouter, HTTPException
from pony.orm import db_session, IntegrityError, TransactionIntegrityError

from core import logger
from core.exceptions import MysteryException
from core.models.games_repository import add_player, get_game_by_name, get_games, new_game
from core.models.player_repository import get_player_by_id
from core.schemas import NewGame, PlayerOutput, GameJoin

games_router = APIRouter()


@games_router.post("/", response_model=PlayerOutput)
def create_game(game: NewGame):
    logger.info(game)
    try:
        if not game.game_name:
            game.game_name = id_generator()
        return new_game(game)
    except TransactionIntegrityError as e:
        logger.error(e)
        raise MysteryException(message="Duplicated Game!", status_code=400)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@games_router.post("/join")
@db_session
def join_to_game(game_join: GameJoin):
    p_id = add_player(game_join.user, game_join.nickname, game_join.name, False)
    game = get_game_by_name(game_join.name)
    player = get_player_by_id(p_id)
    if game:
        game[0].players.add(player[0])
    return game_join


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
