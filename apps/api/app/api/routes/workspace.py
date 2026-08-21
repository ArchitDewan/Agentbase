from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Workspace:
    workspace = Workspace(
        name=payload.name,
        created_at=datetime.now(UTC),
    )

    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)

    return workspace


@router.get("", response_model=list[WorkspaceRead])
async def get_workspaces(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[Workspace]:
    result = await session.execute(
        select(Workspace).order_by(Workspace.created_at.desc())
    )

    return list(result.scalars().all())
