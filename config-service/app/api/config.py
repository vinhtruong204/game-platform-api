from fastapi import APIRouter

from app.routers.weapon import router as weapon_router
from app.routers.character import router as character_router
from app.routers.achievement import router as achievement_router
from app.routers.level_config import router as level_config_router
from app.routers.rank_config import router as rank_config_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(weapon_router)
api_router.include_router(character_router)
api_router.include_router(achievement_router)
api_router.include_router(level_config_router)
api_router.include_router(rank_config_router)
