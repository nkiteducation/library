import pytest
from uuid import uuid4

from database.model import Book, PublishingHouse, BookFile
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_book(session: AsyncSession):
    book = Book(
        id=uuid4(), title="Python 101", desc="Учебник по Python", page_count=350
    )
    session.add(book)
    await session.commit()

    result = await session.get(Book, book.id)
    assert result is not None
    assert result.title == "Python 101"


@pytest.mark.asyncio
async def test_create_publishing_house(session: AsyncSession):
    book = Book(id=uuid4(), title="SQL Mastery", desc="Глубокое погружение в SQL")
    session.add(book)
    await session.commit()

    pub = PublishingHouse(id=uuid4(), name="O'Reilly", lang="en", book_id=book.id)
    session.add(pub)
    await session.commit()

    result = await session.get(PublishingHouse, pub.id)
    assert result is not None
    assert result.name == "O'Reilly"
    assert result.book_id == book.id


@pytest.mark.asyncio
async def test_create_book_file(session: AsyncSession):
    book = Book(id=uuid4(), title="Async Python", desc="Асинхронность в Python")
    session.add(book)
    await session.commit()

    pub = PublishingHouse(id=uuid4(), name="Packt", lang="en", book_id=book.id)
    session.add(pub)
    await session.commit()

    book_file = BookFile(
        id=uuid4(),
        path="/files/async_python.pdf",
        file_type="pdf",
        size=1024,
        pub_id=pub.id,
    )
    session.add(book_file)
    await session.commit()

    result = await session.get(BookFile, book_file.id)
    assert result is not None
    assert result.path == "/files/async_python.pdf"
    assert result.pub_id == pub.id


@pytest.mark.asyncio
async def test_cascade_delete(session: AsyncSession):
    book = Book(id=uuid4(), title="Machine Learning", desc="Основы ML")
    session.add(book)
    await session.commit()

    pub = PublishingHouse(id=uuid4(), name="Springer", lang="en", book_id=book.id)
    session.add(pub)
    await session.commit()

    book_file = BookFile(
        id=uuid4(), path="/files/ml.pdf", file_type="pdf", size=2048, pub_id=pub.id
    )
    session.add(book_file)
    await session.commit()

    await session.delete(book)
    await session.commit()

    book_check = await session.get(Book, book.id)
    pub_check = await session.get(PublishingHouse, pub.id)
    file_check = await session.get(BookFile, book_file.id)

    assert book_check is None
    assert pub_check is None
    assert file_check is None
