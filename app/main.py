"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - validate configuration on startup."""
    get_settings()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="Analyzes onboarding Q&A responses using parallel LLM agents",
        version=settings.app_version,
        lifespan=lifespan,
    )
    
    # Register routes
    app.include_router(router)
    
    # Exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()}
        )
    
    return app


app = create_app()
