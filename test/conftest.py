import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from database.session import SessionManager
from database.model import CoreModel
from main import app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    await SessionManager("sqlite+aiosqlite:///:memory:").init_db(CoreModel.metadata)
    yield
    await SessionManager.close()


@pytest_asyncio.fixture(scope="function")
async def session():
    async with SessionManager.scoped_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
