from fastapi import APIRouter

from app.api.v1.endpoints import auth, photos

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(photos.router, prefix="/photos", tags=["photos"]) 