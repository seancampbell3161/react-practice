"""App factory.

A factory (rather than a module-level `app = FastAPI()`) is what lets the tests
build an app wired to the test database without importing side effects.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware import QueryCountMiddleware
from app.routers import health, reports
from app.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="Interview Prep Lab",
        version="0.1.0",
        description="A lab bench of deliberately broken and deliberately fixed code paths.",
    )

    if settings.expose_query_count:
        app.add_middleware(QueryCountMiddleware)

    # The Vite dev server proxies /api, so CORS is not strictly needed. It is
    # here so you can also hit the API straight from the browser console.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Without this the browser can read the header on same-origin proxied
        # calls but not on cross-origin ones — an easy hour to lose.
        expose_headers=["X-Query-Count"],
    )

    app.include_router(health.router)
    app.include_router(reports.router)
    return app


app = create_app()
