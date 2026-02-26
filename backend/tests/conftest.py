from collections.abc import AsyncGenerator

import pytest
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import Base
from app.models import *  # noqa: F401, F403 — register all models for create_all

# Use a separate test database to avoid clobbering dev data.
# Falls back to the default URL if TEST_DATABASE_URL is not set.
TEST_DATABASE_URL = settings.database_url

# NullPool ensures each test gets fresh connections (no stale event-loop bindings).
engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session


@pytest.fixture
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    r = aioredis.from_url(settings.redis_url, decode_responses=True)
    yield r
    await r.flushdb()
    await r.aclose()


@pytest.fixture
async def client(
    db_session: AsyncSession, redis_client: aioredis.Redis
) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient that uses the test DB session and a real Redis."""
    from app.api.auth import get_db, get_redis
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_redis] = lambda: redis_client

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
