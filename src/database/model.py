import re
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from database.mixin import TimestampMixin, UUIDMixin
from database.typing import SizeType


def camel_to_snake(name: str) -> str:
    """Преобразует CamelCase в snake_case."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class CoreModel(DeclarativeBase, AsyncAttrs):
    """Базовая модель с автоматическим `__tablename__`."""

    @declared_attr
    def __tablename__(self) -> str:
        return camel_to_snake(self.__name__)


class Book(CoreModel, UUIDMixin, TimestampMixin):
    """Модель книги."""

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    desc: Mapped[str | None] = mapped_column(String, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    pubs: Mapped[list["PublishingHouse"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PublishingHouse(CoreModel, UUIDMixin, TimestampMixin):
    """Модель издательства."""

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    lang: Mapped[str] = mapped_column(String(50), nullable=False)

    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), nullable=False
    )
    book: Mapped["Book"] = relationship(back_populates="pubs")

    files: Mapped[list["BookFile"]] = relationship(
        back_populates="pub",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BookFile(CoreModel, UUIDMixin, TimestampMixin):
    """Модель файла книги."""

    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[SizeType] = mapped_column(Integer, nullable=False)

    pub_id: Mapped[UUID] = mapped_column(
        ForeignKey("publishing_house.id", ondelete="CASCADE"), nullable=False
    )
    pub: Mapped["PublishingHouse"] = relationship(back_populates="files")
