from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal, engine
from app.models.workspace import Workspace
from main import app


@pytest_asyncio.fixture(autouse=True)
async def clean_workspaces() -> AsyncGenerator[None]:
    await engine.dispose()

    async with AsyncSessionLocal() as session:
        await session.execute(delete(Workspace))
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(delete(Workspace))
        await session.commit()

    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
