import random
import string
from typing import List
from uuid import UUID

from fastapi import APIRouter
from pony.orm import TransactionIntegrityError

from core import logger
from core.exceptions import MysteryException
from core.repositories import get_games, new_game
from core.schemas import NewGame, GameJoin, GameListPlayers, GamePlayer
from core.schemas.games_schema import GameBasicInfo, BasicGameInput
from core.services import start_new_game, find_game_hide_player_id, join_player


games_router = APIRouter()


@games_router.post("/", response_model=GamePlayer, status_code=201)
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


@games_router.put("/join", response_model=GamePlayer)
def join_to_game(game_join: GameJoin):
    logger.info(game_join)
    return join_player(game_join)


@games_router.get("/{id}", response_model=GameListPlayers)
def find_game_by_id(id: UUID):
    return find_game_hide_player_id(id)


@games_router.get("/", response_model=List[GameBasicInfo])
def get_all_available_games():
    return [GameBasicInfo(name=row[0], player_count=row[1], started=row[2]) for row in get_games()]


@games_router.put("/start", response_model=GameListPlayers)
async def start_created_game(game: BasicGameInput):
    return await start_new_game(game)



