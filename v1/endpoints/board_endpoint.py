from typing import List
from fastapi import APIRouter
from core.repositories import get_board
from core.schemas.board_schema import RowOutput


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

