from typing import Dict

from fastapi import APIRouter
from core.repositories.board_repository import get_board, get_complete_row, get_adjacent_boxes
from core.schemas.board_schema import BoardOutput

board_router = APIRouter()


@board_router.get("/")
def get_complete_board(response_model=BoardOutput):
    return get_board()


@board_router.get("/row/{id}")
def get_complete_board(id: int):
    return get_complete_row(id)


@board_router.get("/box/adj/{id}")
def get_complete_board(id: int):
    return get_adjacent_boxes(id)
