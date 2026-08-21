"""Async engine, session factory, and the session-per-request dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.query_count import install_query_counter
from app.settings import Settings, get_settings


def build_engine(settings: Settings | None = None) -> AsyncEngine:
    settings = settings or get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.echo_sql,
        # pool_pre_ping saves you from the "server closed the connection
        # unexpectedly" that follows a `docker compose restart db`.
        pool_pre_ping=True,
    )
    install_query_counter(engine)
    return engine


engine: AsyncEngine = build_engine()

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Session-per-request.

    Phase 5 replaces this with an ``async with session.begin()`` variant so the
    transaction boundary is the request boundary (commit on success, rollback on
    raise). For now it is the plain version so Phase 0 stays readable.
    """
    async with SessionLocal() as session:
        yield session
