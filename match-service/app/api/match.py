from fastapi import APIRouter

from app.routers.map import router as map_router
from app.routers.mode import router as mode_router
from app.routers.match_history import router as match_history_router
from app.routers.match_player import router as match_player_router
from app.routers.matchmaking import router as matchmaking_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(map_router)
api_router.include_router(mode_router)
api_router.include_router(match_history_router)
api_router.include_router(match_player_router)
api_router.include_router(matchmaking_router)
