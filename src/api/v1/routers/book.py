import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from api.v1.schemas import BookCreate, BookRead, BookUpdate
from database.session import SessionManager
from database.model import Book
from sqlalchemy import insert, select, update, delete

logger = logging.getLogger(__name__)

book_router = APIRouter(prefix="/book", tags=["Book"])


@book_router.post("/", response_model=BookRead)
async def create_book(new_book: BookCreate):
    logger.info("Starting to create a book: %s", new_book)
    async with SessionManager.scoped_session() as session:
        stmt = insert(Book).values(**new_book.model_dump()).returning(Book)
        book = await session.scalar(stmt)
        await session.commit()
    if book:
        logger.info("Book created successfully with id: %s", book.id)
    else:
        logger.error("Error creating book: %s", new_book)
    return BookRead.model_validate(book)


@book_router.get("/", response_model=list[BookRead])
async def list_books():
    logger.info("Fetching list of books")
    async with SessionManager.scoped_session() as session:
        stmt = select(Book)
        books = (await session.scalars(stmt)).all()
    if not books:
        logger.info("No books found")
        return []
    logger.info("Fetched %s books", len(books))
    return [BookRead.model_validate(book) for book in books]


@book_router.get("/{id}", response_model=BookRead)
async def get_book(id: UUID):
    logger.info("Fetching book with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = select(Book).where(Book.id == id)
        book = await session.scalar(stmt)
    if not book:
        logger.warning("Book with id %s not found", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    logger.info("Book with id %s found", id)
    return BookRead.model_validate(book)


@book_router.put("/{id}", response_model=BookRead)
async def update_book(id: UUID, update_book: BookUpdate):
    logger.info("Updating book with id: %s. New data: %s", id, update_book)
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
        logger.warning("Book with id %s not found for update", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    logger.info("Book with id %s updated successfully", id)
    return BookRead.model_validate(book)


@book_router.delete("/{id}", response_model=str)
async def delete_book(id: UUID):
    logger.info("Deleting book with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = delete(Book).where(Book.id == id).returning(Book.id)
        result = await session.execute(stmt)
        await session.commit()
    deleted_id = result.scalar()
    if not deleted_id:
        logger.warning("Book with id %s not found for deletion", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    logger.info("Book with id %s deleted successfully", id)
    return "OK"
