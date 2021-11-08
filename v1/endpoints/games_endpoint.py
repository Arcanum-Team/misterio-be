import random
import string
from typing import List
from uuid import UUID

from fastapi import APIRouter
from pony.orm import TransactionIntegrityError, ObjectNotFound

from core import logger
from core.exceptions import MysteryException
from core.repositories import join_player_to_game, get_games, new_game, pass_turn
from core.schemas import NewGame, PlayerOutput, GameJoin, GameOutput, GamePassTurn
from core.schemas.games_schema import GameBasicInfo, GameStart
from core.services import start_new_game, find_game_hide_player_id

games_router = APIRouter()


@games_router.post("/", response_model=PlayerOutput, status_code=201)
def create_game(game: NewGame):
    logger.info(game)
    try:
        if not game.game_name:
            game.game_name = id_generator()
        return PlayerOutput.from_orm(new_game(game))
    except TransactionIntegrityError as e:
        logger.error(e)
        raise MysteryException(message="Duplicated Game!", status_code=400)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@games_router.put("/join", response_model=PlayerOutput)
def join_to_game(game_join: GameJoin):
    logger.info(game_join)
    return PlayerOutput.from_orm(join_player_to_game(game_join))


@games_router.get("/{id}", response_model=GameOutput)
def find_game_by_id(id: UUID):
    return find_game_hide_player_id(id)


@games_router.get("/", response_model=List[GameBasicInfo])
def get_all_available_games():
    return [GameBasicInfo(name=row[0], player_count=row[1], started=row[2]) for row in get_games()]


@games_router.put("/start", response_model=GameOutput)
def start_created_game(game: GameStart):
    return start_new_game(game)


@games_router.put("/pass_turn", response_model=GameOutput)
def pass_game_turn(game: GamePassTurn):
    try:
        return pass_turn(game.game_id)
    except ObjectNotFound:
        logger.error("Game not found [%s]", game.game_id)
        raise MysteryException(message="Game not found!", status_code=404)
