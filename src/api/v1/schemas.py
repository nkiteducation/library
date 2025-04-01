from datetime import datetime
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
    desc: str
    page_count: int


class BookRead(BookCreate, BaseReadSchemas):
    pubs: list["PublishingHouseRead"]


###PublishingHouse###
class PublishingHouseCreate(BaseModel):
    name: str
    lang: str


class PublishingHouseRead(PublishingHouseCreate, BaseReadSchemas):
    files: list["BookFile"]


###BookFile###
class BookFile(BaseModel):
    file_type: str
    size: ByteSize
