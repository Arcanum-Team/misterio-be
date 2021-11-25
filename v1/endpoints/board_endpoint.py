from fastapi import APIRouter
from core.services import get_complete_board
from core.services.shifts_service import get_possible_movement

board_router = APIRouter()


@board_router.get("/")
def get_board():
    return get_complete_board()
