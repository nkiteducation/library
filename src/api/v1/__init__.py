from fastapi import APIRouter
from api.v1.routers.book import book_router

v1_router = APIRouter(prefix="/V1")
v1_router.include_router(book_router)
