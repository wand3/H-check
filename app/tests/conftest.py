import pytest
import asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app  # your FastAPI app which includes routes/auth
from app.database.db_engine import get_session  # we will override this

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:ma3str0@localhost:5432/hcheck"

test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# Override dependency
async def override_get_session():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    # create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await test_engine.dispose()

@pytest.fixture
async def async_client(monkeypatch):
    # patch the dependency
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app, base_url="http://") as client:
        yield client

    app.dependency_overrides.pop(get_session, None)