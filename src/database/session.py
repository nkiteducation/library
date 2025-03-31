import asyncio
import logging
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

LOG = logging.getLogger(__name__)


class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init(*args, **kwargs)
        return cls._instance

    def __init(self, url: str = "sqlite+aiosqlite:///:memory:", **kwargs):
        LOG.debug("Initializing with DB URL: %s", url)
        self.async_engine = create_async_engine(
            url, echo=kwargs.get("echo", False), future=True
        )
        self.async_session_factory = async_sessionmaker(
            self.async_engine, autoflush=False, expire_on_commit=False
        )
        self.scoped_factory = async_scoped_session(
            self.async_session_factory, scopefunc=lambda: asyncio.current_task()
        )

    @classmethod
    @asynccontextmanager
    async def scoped_session(cls):
        session: AsyncSession = cls._instance.scoped_factory()
        LOG.debug("Session created: %s", session)
        try:
            yield session
        except Exception as e:
            LOG.warning("Session error: %s", e, exc_info=True)
            await session.rollback()
        finally:
            await cls._instance.scoped_factory.remove()
            LOG.debug("Session removed: %s", session)

    @classmethod
    async def init_db(cls, metadata: MetaData) -> None:
        LOG.info("Initializing database")
        async with cls._instance.async_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    @classmethod
    async def close(cls) -> None:
        LOG.debug("Closing database connection")
        await cls._instance.async_engine.dispose()