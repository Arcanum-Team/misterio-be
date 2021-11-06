from logging import exception, log
from typing import List
from fastapi import APIRouter
from core.models.board_repository import get_board
from core.schemas.board_schema import RowOutput
from core.schemas.games_schema import GamePassTurn, GameOutput
from core.models.games_repository import find_complete_game
from pony.orm import ObjectNotFound
from core.settings import logger
from core.exceptions import MysteryException


board_router = APIRouter()

@board_router.get("/")
def get_complete_board(response_model=List[RowOutput]):
    # g : GameOutput
    # try:
    #     g = find_complete_game(game_id.game_id)
    # except Exception:
    #     logger.error("Game not found [{}]".format(game_id.game_id))
    #     raise MysteryException(message="Game not found!", status_code=404)
    # if not g.started:
    #     raise MysteryException(message="Game isnt started", status_code=400)
    
    return get_board()

