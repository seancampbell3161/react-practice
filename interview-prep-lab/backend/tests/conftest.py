"""Test harness: a real Postgres, a per-test transaction, and a query budget.

Deliberately not SQLite. Several exercises in this lab (JSONB, SELECT FOR UPDATE,
real CHECK/FK behaviour, deep-offset cost) only behave honestly on Postgres, and
a test suite that passes on a database you do not ship is a test suite that lies.

Isolation strategy: each test gets a connection with an open transaction, and the
session joins it via a SAVEPOINT (``join_transaction_mode="create_savepoint"``).
Application code can call ``commit()`` normally; the outer transaction is rolled
back afterwards, so nothing leaks between tests.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

import asyncpg
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.db import get_session
from app.main import create_app
from app.models import Base, Org, Report, User
from app.query_count import QueryCounter, count_queries, install_query_counter
from app.settings import get_settings


async def _ensure_database(url: str) -> None:
    """CREATE DATABASE lab_test if it is not there yet."""
    parsed = make_url(url)
    assert parsed.database is not None
    conn = await asyncpg.connect(
        host=parsed.host,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", parsed.database
        )
        if not exists:
            # Identifier, so it cannot be parameterised; the name comes from our
            # own settings, not from user input.
            await conn.execute(f'CREATE DATABASE "{parsed.database}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    url = get_settings().test_database_url
    await _ensure_database(url)

    engine = create_async_engine(url, poolclass=None)
    install_query_counter(engine)

    # TODO(interview-prep): Phase 9 swaps create_all for `alembic upgrade head`
    # so the suite also proves the migrations produce the schema the models
    # describe. Until then a bad migration would pass the tests.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()
    session = AsyncSession(
        bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
    )
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()


@pytest.fixture
def app(session: AsyncSession) -> FastAPI:
    """The real app, with the request session swapped for the test's session.

    ``dependency_overrides`` is the seam that makes this possible — the endpoints
    are untouched and unaware.
    """
    application = create_app()

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    application.dependency_overrides[get_session] = override_get_session
    return application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://lab.test") as ac:
        yield ac


@pytest.fixture
def assert_max_queries() -> Callable[[int], Iterator[QueryCounter]]:
    """Fail the test if the block inside issues more than ``n`` statements.

    This is the other half of the X-Query-Count header: the same counter, turned
    into an assertion. Use it to pin a query budget on an endpoint so a future
    refactor that reintroduces an N+1 breaks the build instead of the latency
    graph.

        with assert_max_queries(2):
            await client.get("/reports")
    """

    @contextmanager
    def _assert_max_queries(n: int) -> Iterator[QueryCounter]:
        with count_queries() as counter:
            yield counter
        if counter.count > n:
            sample = "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(counter.statements[:10]))
            raise AssertionError(
                f"expected at most {n} queries, got {counter.count}\nfirst statements:\n{sample}"
            )

    return _assert_max_queries  # type: ignore[return-value]


@pytest_asyncio.fixture
async def two_orgs(session: AsyncSession) -> dict[str, object]:
    """Two orgs, two users each, three reports each — the smallest dataset that
    can still demonstrate a cross-tenant leak."""
    made: dict[str, object] = {}
    for slug in ("acme", "globex"):
        org = Org(id=uuid.uuid4(), name=f"{slug.title()} Test")
        session.add(org)
        await session.flush()

        users = [
            User(
                id=uuid.uuid4(),
                org_id=org.id,
                email=f"{name}@{slug}.test",
                hashed_password="unhashed$placeholder",
                role=role,
            )
            for name, role in (("ada", "admin"), ("brice", "member"))
        ]
        session.add_all(users)
        await session.flush()

        reports = [
            Report(
                id=uuid.uuid4(),
                org_id=org.id,
                author_id=users[i % len(users)].id,
                title=f"{slug} report {i}",
                body="body",
                status="draft",
                cost_cents=1000 + i,
                internal_notes=f"INTERNAL {slug} {i}",
                created_at=datetime(2026, 1, 1, 12, i, tzinfo=UTC),
            )
            for i in range(3)
        ]
        session.add_all(reports)
        await session.flush()

        made[slug] = {"org": org, "users": users, "reports": reports}
    return made
