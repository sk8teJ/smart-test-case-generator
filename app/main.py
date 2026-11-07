from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.test_cases import router as test_cases_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "Generate structured API test scenarios from OpenAPI specifications. "
        "The current generator uses deterministic rules and validates its output."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(test_cases_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }
