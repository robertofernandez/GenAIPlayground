from fastapi import FastAPI

from app.api.v1.routes import router as v1_router
from app.core.config import settings
from app.api.v1.test_routes import router as test_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(v1_router, prefix="/api/v1")
    if settings.ENVIRONMENT in ["testing", "development"]:
        print("🚀 adding test routes...")
        app.include_router(test_router)
    return app


app = create_app()
