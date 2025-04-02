import sys
from pathlib import Path

import pytest_asyncio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database.session import SessionManager
from database.model import CoreModel


@pytest_asyncio.fixture(scope="session")
async def init_db():
    await SessionManager("sqlite+aiosqlite:///:memory:").init_db(CoreModel.metadata)
    yield
    await SessionManager.close()


@pytest_asyncio.fixture(scope="function")
async def session(init_db):
    async with SessionManager.scoped_session() as session:
        yield session
