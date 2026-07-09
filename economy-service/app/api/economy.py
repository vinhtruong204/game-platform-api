from fastapi import APIRouter

from app.routers.shop import router as shop_router
from app.routers.lucky_wheel import router as lucky_wheel_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(shop_router)
api_router.include_router(lucky_wheel_router)
