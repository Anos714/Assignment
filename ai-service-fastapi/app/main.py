from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Knowledge Base RAG Service",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
