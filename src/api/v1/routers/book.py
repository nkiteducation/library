import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from api.v1.dependencies import rate_limiter
from api.v1.schemas import BookCreate, BookRead, BookUpdate
from database.session import SessionManager
from database.model import Book
from sqlalchemy import insert, select, update, delete

logger = logging.getLogger(__name__)

book_router = APIRouter(
    prefix="/book", tags=["📚 Book Management"], dependencies=[Depends(rate_limiter)]
)


@book_router.post(
    "/",
    response_model=BookRead,
    summary="Create a new book 📖",
    description="Create a new book record with title, author, and other details. ✍️",
)
async def create_book(new_book: BookCreate):
    logger.info("Starting to create a book: %s", new_book)
    async with SessionManager.scoped_session() as session:
        stmt = insert(Book).values(**new_book.model_dump()).returning(Book)
        book = await session.scalar(stmt)
        await session.commit()

    logger.info("Book created successfully with id: %s", book.id)
    return BookRead.model_validate(book)


@book_router.get(
    "/",
    response_model=list[BookRead],
    summary="List all books 📚",
    description="Retrieve a list of all books available in the library. 📖",
)
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


@book_router.get(
    "/{id}",
    response_model=BookRead,
    summary="Get book details 📖",
    description="Retrieve details of a specific book by its ID. 🔍",
)
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


@book_router.put(
    "/{id}",
    response_model=BookRead,
    summary="Update a book ✏️",
    description="Update the details of an existing book by its ID. 🛠️",
)
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


@book_router.delete(
    "/{id}",
    response_model=dict,
    summary="Delete a book 🗑️",
    description="Delete a book from the system by its ID. 🛑",
)
async def delete_book(id: UUID):
    logger.info("Deleting book with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = delete(Book).where(Book.id == id).returning(Book.id)
        deleted_id = await session.scalar(stmt)
        await session.commit()

    if not deleted_id:
        logger.warning("Book with id %s not found for deletion", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    logger.info("Book with id %s deleted successfully", id)

    return {
        "message": "Book successfully deleted. 📚",
        "deleted_book_id": deleted_id,
    }
