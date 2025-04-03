from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, ByteSize


class BaseReadSchemas(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


###BOOK###
class BookCreate(BaseModel):
    title: str
    author: str
    desc: str
    page_count: int


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    desc: Optional[str] = None
    page_count: Optional[int] = None


class BookRead(BookCreate, BaseReadSchemas):
    pubs: list["PublishingHouseRead"]


###PublishingHouse###
class PublishingHouseCreate(BaseModel):
    name: str
    lang: str


class PublishingHouseRead(PublishingHouseCreate, BaseReadSchemas):
    files: list["BookFileRead"]


###BookFile###
class BookFileRead(BaseReadSchemas):
    file_type: str
    size: ByteSize
