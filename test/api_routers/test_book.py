import pytest
from httpx import AsyncClient
from fastapi import status
from api.v1.schemas import BookCreate, BookRead


@pytest.fixture(scope="session")
def book():
    return BookCreate(
        title="titleTest",
        author="authorTest",
        desc="descTest",
        page_count=10,
    )


@pytest.mark.asyncio
async def test_list_books_empty(client: AsyncClient):
    response = await client.get("/V1/book/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_book_not_found(client: AsyncClient):
    response = await client.get("/V1/book/00000000-0000-0000-0000-000000000000")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_book_not_found(client: AsyncClient, book: BookCreate):
    response = await client.put(
        "/V1/book/00000000-0000-0000-0000-000000000000", json=book.model_dump()
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_book_not_found(client: AsyncClient):
    response = await client.delete("/V1/book/00000000-0000-0000-0000-000000000000")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_book(client: AsyncClient, book: BookCreate):
    response = await client.post(
        "/V1/book/",
        json=book.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_list_books(client: AsyncClient, book: BookCreate):
    response = await client.get("/V1/book/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]["title"] == book.title
    assert data[0]["author"] == book.author
    assert data[0]["desc"] == book.desc
    assert data[0]["page_count"] == book.page_count


@pytest.mark.asyncio
async def test_get_book(client: AsyncClient, book: BookCreate):
    create_response = await client.post("/V1/book/", json=book.model_dump())
    book_id = create_response.json()["id"]

    response = await client.get(f"/V1/book/{book_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == book.title
    assert data["author"] == book.author
    assert data["desc"] == book.desc
    assert data["page_count"] == book.page_count


@pytest.mark.asyncio
async def test_update_book(client: AsyncClient, book: BookCreate):
    create_response = await client.post("/V1/book/", json=book.model_dump())
    book_id = create_response.json()["id"]

    update_bata = book.model_dump()
    update_bata.update(
        title="Python к вершинам марсерства",
        author="Лусиану Рамальо",
        desc="bla bla bla",
        page_count=881,
    )

    response = await client.put(f"/V1/book/{book_id}", json=update_bata)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["title"] == update_bata["title"]
    assert data["author"] == update_bata["author"]
    assert data["desc"] == update_bata["desc"]
    assert data["page_count"] == update_bata["page_count"]


@pytest.mark.asyncio
async def test_delete_book(client: AsyncClient, book: BookCreate):
    create_response = await client.post("/V1/book/", json=book.model_dump())
    book_id = create_response.json()["id"]

    response = await client.delete(f"/V1/book/{book_id}")
    assert response.status_code == status.HTTP_200_OK
