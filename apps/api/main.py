from fastapi import FastAPI

from app.api.routes.db_health import router as db_health_router
from app.api.routes.health import router as health_router
from app.api.routes.workspace import router as workspace_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
    )

    app.include_router(health_router)
    app.include_router(db_health_router)
    app.include_router(workspace_router)

    return app


app = create_app()
