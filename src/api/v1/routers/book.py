from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from api.v1.dependencies import process_request_body
from api.v1.schemas import BookCreate, BookRead, BookUpdate
from database.session import SessionManager
from database.model import Book
from sqlalchemy import insert, select, update, delete

book_router = APIRouter(prefix="/book", tags=["Book"])


@book_router.post("/", response_model=BookRead)
async def create_book(new_book: BookCreate):
    async with SessionManager.scoped_session() as session:
        stmt = insert(Book).values(**new_book.model_dump()).returning(Book)
        book = await session.scalar(stmt)
        await session.commit()

    return BookRead.model_validate(book)


@book_router.get("/{id}", response_model=BookRead)
async def get_book(id: UUID):
    async with SessionManager.scoped_session() as session:
        stmt = select(Book).where(Book.id == id)
        book = await session.scalar(stmt)

    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return BookRead.model_validate(book)


@book_router.put("/{id}", response_model=BookRead)
async def update_book(id: UUID, update_book: BookUpdate):
    async with SessionManager.scoped_session() as session:
        stmt = (
            update(Book)
            .where(Book.id == id)
            .values(**update_book.model_dump(exclude_none=True))
            .returning(Book)
        )
        book = await session.scalar(stmt)
        await session.commit()

    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return BookRead.model_validate(book)


@book_router.delete("/{id}", response_model=str)
async def delete_book(id: UUID):
    async with SessionManager.scoped_session() as session:
        stmt = delete(Book).where(Book.id == id).returning(Book.id)
        id = await session.execute(stmt)
        await session.commit()

    if not id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return "OK"
