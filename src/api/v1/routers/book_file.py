import logging
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import insert

from api.v1.dependencies import rate_limiter
from api.v1.schemas import BookFileRead
from database.session import SessionManager
from database.model import BookFile
from utils.file import FileManager


logger = logging.getLogger(__name__)

book_file_router = APIRouter(
    prefix="/book-file",
    tags=["Book File Management"],
    dependencies=[Depends(rate_limiter)],
)


@book_file_router.post("/{publishing_house_id}")
async def create_book_file(publishing_house_id: UUID, file: UploadFile):
    path = await FileManager.reading(file.filename, file)
    async with SessionManager.scoped_session() as session:
        stmt = (
            insert(BookFile)
            .values(
                path=str(path),
                file_type=path.suffix,
                size=file.size,
                pub_id=publishing_house_id,
            )
            .returning(BookFile)
        )
        pub = await session.scalar(stmt)
        await session.commit()

    return BookFileRead.model_validate(pub)
