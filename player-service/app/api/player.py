from fastapi import APIRouter

from app.routers.player_profile import router as player_profile_router
from app.routers.player_stats import router as player_stats_router
from app.routers.player_currency import router as player_currency_router
from app.routers.player_inventory import router as player_inventory_router
from app.routers.player_equipment import router as player_equipment_router
from app.routers.player_selected_character import router as player_selected_character_router
from app.routers.player_achievement import router as player_achievement_router
from app.routers.player_rank import router as player_rank_router
from app.routers.purchase import router as purchase_router
from app.routers.auth import router as auth_router
from app.routers.leaderboard import router as leaderboard_router
from app.routers.spin import router as spin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(player_profile_router)
api_router.include_router(player_stats_router)
api_router.include_router(player_currency_router)
api_router.include_router(player_inventory_router)
api_router.include_router(player_equipment_router)
api_router.include_router(player_selected_character_router)
api_router.include_router(player_achievement_router)
api_router.include_router(player_rank_router)
api_router.include_router(purchase_router)
api_router.include_router(leaderboard_router)
api_router.include_router(spin_router)
