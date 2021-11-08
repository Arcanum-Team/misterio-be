from fastapi import APIRouter
from core.schemas.board_schema import BoardOutput
from core.services import get_complete_board
from core.services.shifts_service import find_possible_movements

board_router = APIRouter()


@board_router.get("/")
def get_board(response_model=BoardOutput):
    return get_complete_board()


@board_router.get("/box/adj/{id}/{dado}")
def get_adjacent_boxes(id: int, dado: int):
    result = find_possible_movements(dado, id, -1)
    result.discard(id)
    return result
