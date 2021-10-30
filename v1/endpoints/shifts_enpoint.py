from fastapi import APIRouter

from core.schemas import Movement

shifts_router = APIRouter()


@shifts_router.put("/move")
def move_player(movement: Movement):
    pass
