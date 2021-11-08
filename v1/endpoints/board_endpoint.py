from fastapi import APIRouter
from core.schemas.board_schema import BoardOutput
from core.services import get_complete_board
from core.services.shifts_service import get_possible_movement

board_router = APIRouter()


@board_router.get("/")
def get_board(response_model=BoardOutput):
    return get_complete_board()


@board_router.get("/box/adj/{id}/{dice}")
def get_adjacent_boxes(id: int, dice: int):
    return get_possible_movement(dice, id)
