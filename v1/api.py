from fastapi import APIRouter

from v1.endpoints import games_router, shifts_router

api_router = APIRouter()

api_router.include_router(games_router, prefix="/games", tags=["Game"])
api_router.include_router(shifts_router, prefix="/shifts", tags=["Shifts"])
