import logging
import random
import string
from typing import List
from uuid import UUID

from fastapi import APIRouter
from pony.orm import db_session, TransactionIntegrityError, ObjectNotFound

from core import logger
from core.exceptions import MysteryException
from core.models import join_player_to_game, get_games, new_game, games_repository
from core.schemas import NewGame, PlayerOutput, GameJoin, GameOutput
from core.schemas.games_schema import GameBasicInfo

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
    try:
        return PlayerOutput.from_orm(join_player_to_game(game_join))
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game_join.game_id))
        raise MysteryException(message="Game not found!", status_code=404)


@games_router.get("/{id}", response_model=GameOutput)
def find_game_by_id(id: UUID):
    return find_complete_game(id)


@db_session
def find_complete_game(id):
    return GameOutput.from_orm(games_repository.find_game_by_id(id))


@games_router.get("/", response_model=List[GameBasicInfo])
def get_all_available_games():

    return [GameBasicInfo(name=row[0], player_count=row[1], started=row[2]) for row in get_games()]


@games_router.put("/start/{gameName}/{host_id}")
@db_session
def start_game(game_name: str, host_id: int):
    start_game(game_name, host_id)
