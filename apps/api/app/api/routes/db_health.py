from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health/db")
async def db_health_check(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
