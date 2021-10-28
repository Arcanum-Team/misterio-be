from fastapi import APIRouter

from core.schemas.player_schema import PlayerOrder

player_router = APIRouter()


@player_router.put("/order")
def read_root(player: PlayerOrder):
    return player
