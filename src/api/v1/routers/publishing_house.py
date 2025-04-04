import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from api.v1.dependencies import rate_limiter
from api.v1.schemas import (
    PublishingHouseCreate,
    PublishingHouseRead,
    PublishingHouseUpdate,
)
from database.session import SessionManager
from sqlalchemy import insert, select, update, delete
from database.model import PublishingHouse

logger = logging.getLogger(__name__)

publishing_house_router = APIRouter(
    prefix="/publishing-house",
    tags=["🏢 Publishing House Management"],
    dependencies=[Depends(rate_limiter)],
)


@publishing_house_router.post(
    "/{book_id}",
    response_model=PublishingHouseRead,
    summary="Create a new publishing house 🏢",
    description="Add a new publishing house record linked to a specific book. 📚",
)
async def create_publishing_house(
    book_id: UUID, new_publishing_house: PublishingHouseCreate
):
    logger.info("Creating publishing house for book_id: %s", book_id)
    async with SessionManager.scoped_session() as session:
        stmt = (
            insert(PublishingHouse)
            .values(book_id=book_id, **new_publishing_house.model_dump())
            .returning(PublishingHouse)
        )
        publishing_house = await session.scalar(stmt)
        await session.commit()

    logger.info("Publishing house created with id: %s", publishing_house.id)
    return PublishingHouseRead.model_validate(publishing_house)


@publishing_house_router.get(
    "/",
    response_model=list[PublishingHouseRead],
    summary="List all publishing houses 🏢",
    description="Retrieve a list of all registered publishing houses. 📋",
)
async def list_publishing_houses():
    logger.info("Fetching all publishing houses")
    async with SessionManager.scoped_session() as session:
        stmt = select(PublishingHouse)
        publishing_houses = (await session.scalars(stmt)).all()

    if not publishing_houses:
        logger.info("No publishing houses found")
        return []

    logger.info("Fetched %s publishing houses", len(publishing_houses))
    return [
        PublishingHouseRead.model_validate(publishing_house)
        for publishing_house in publishing_houses
    ]


@publishing_house_router.get(
    "/{id}",
    response_model=PublishingHouseRead,
    summary="Get publishing house details 🏛️",
    description="Retrieve details of a specific publishing house by its ID. 🔍",
)
async def get_publishing_house(id: UUID):
    logger.info("Fetching publishing house with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = select(PublishingHouse).where(PublishingHouse.id == id)
        publishing_house = await session.scalar(stmt)

    if not publishing_house:
        logger.warning("Publishing house with id %s not found", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    logger.info("Publishing house with id %s found", id)
    return PublishingHouseRead.model_validate(publishing_house)


@publishing_house_router.put(
    "/{id}",
    response_model=PublishingHouseRead,
    summary="Update a publishing house ✏️",
    description="Modify the details of an existing publishing house. 🛠️",
)
async def update_publishing_house(
    id: UUID,
    book_id: Optional[UUID] = Query(None),
    update_book: Optional[PublishingHouseUpdate] = Body(None),
):
    logger.info("Updating publishing house with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = (
            update(PublishingHouse)
            .where(PublishingHouse.id == id)
            .values(**update_book.model_dump(exclude_none=True), book_id=book_id)
            .returning(PublishingHouse)
        )
        publishing_house = await session.scalar(stmt)
        await session.commit()

    if not publishing_house:
        logger.warning("Publishing house with id %s not found", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    logger.info("Publishing house with id %s updated successfully", id)
    return PublishingHouseRead.model_validate(publishing_house)


@publishing_house_router.delete(
    "/{id}",
    response_model=dict,
    summary="Delete a publishing house 🗑️",
    description="Remove a publishing house record by its ID. 🚫",
)
async def delete_publishing_house(id: UUID):
    logger.info("Deleting publishing house with id: %s", id)
    async with SessionManager.scoped_session() as session:
        stmt = (
            delete(PublishingHouse)
            .where(PublishingHouse.id == id)
            .returning(PublishingHouse.id)
        )
        deleted_id = await session.scalar(stmt)
        await session.commit()

    if not deleted_id:
        logger.warning("Publishing house with id %s not found for deletion", id)
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    logger.info("Publishing house with id %s deleted successfully", id)
    return {
        "message": "Publishing house successfully deleted. 🏢",
        "deleted_publishing_house_id": deleted_id,
    }
