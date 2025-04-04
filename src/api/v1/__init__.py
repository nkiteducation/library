from fastapi import APIRouter
from api.v1.routers.book import book_router
from api.v1.routers.publishing_house import publishing_house_router
from api.v1.routers.book_file import book_file_router

v1_router = APIRouter(prefix="/V1")
v1_router.include_router(book_router)
v1_router.include_router(publishing_house_router)
v1_router.include_router(book_file_router)
