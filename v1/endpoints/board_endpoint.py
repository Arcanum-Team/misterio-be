from fastapi import APIRouter
from core.repositories.board_repository import get_board
from core.schemas.board_schema import BoardOutput

board_router = APIRouter()


@board_router.get("/")
def get_complete_board(response_model=BoardOutput):
    return get_board()
