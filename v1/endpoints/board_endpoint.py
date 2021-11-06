from logging import exception, log
from typing import List
from fastapi import APIRouter
from core.models.board_repository import get_board
from core.schemas.board_schema import BoardOutput, RowOutput
from core.schemas.games_schema import GamePassTurn, GameOutput
from core.models.games_repository import find_complete_game
from core.settings import logger
from core.exceptions import MysteryException


board_router = APIRouter()

@board_router.get("/")
def get_complete_board(response_model=BoardOutput):
    return get_board()

