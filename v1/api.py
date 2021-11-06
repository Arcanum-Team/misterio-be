from fastapi import APIRouter

from v1.endpoints import games_router, shifts_router, cards_router, board_router

api_router = APIRouter()

api_router.include_router(board_router, prefix="/board", tags=["Board"])
api_router.include_router(cards_router, prefix="/cards", tags=["Card"])
api_router.include_router(games_router, prefix="/games", tags=["Game"])
api_router.include_router(shifts_router, prefix="/shifts", tags=["Shifts"])
