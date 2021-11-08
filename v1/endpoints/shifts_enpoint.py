from fastapi import APIRouter

from core.schemas import Movement
from core.services import move_player_service

shifts_router = APIRouter()


@shifts_router.put("/move")
def move_player(movement: Movement):
    return move_player_service(movement)
