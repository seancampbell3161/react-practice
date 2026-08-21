"""Phase 0 acceptance: the instruments themselves work.

Everything later in the lab is measured with these two tools, so they get their
own tests. If `assert_max_queries` silently counted nothing, every query-budget
test after it would be a green light wired to nothing.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Report


async def test_health_reports_db_connectivity(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": True}


async def test_every_response_carries_the_query_count_header(client: AsyncClient) -> None:
    response = await client.get("/health")
    # /health runs exactly one statement: SELECT 1.
    assert response.headers["X-Query-Count"] == "1"


async def test_reports_list_stays_within_its_query_budget(
    client: AsyncClient,
    two_orgs: dict[str, Any],
    assert_max_queries: Callable[[int], Any],
) -> None:
    """selectinload() means the cost is flat: one query for reports, one for
    authors, regardless of how many rows come back."""
    with assert_max_queries(2) as counter:
        response = await client.get("/reports?limit=6")

    assert response.status_code == 200
    assert len(response.json()) == 6
    assert counter.count == 2
    # The header and the fixture are reading the same counter, by construction.
    assert response.headers["X-Query-Count"] == "2"


async def test_query_budget_fixture_actually_fails_when_exceeded(
    session: Any,
    two_orgs: dict[str, Any],
    assert_max_queries: Callable[[int], Any],
) -> None:
    """The negative case. A lazy load per row is exactly the Phase 1 bug, and the
    budget fixture has to be the thing that catches it."""
    reports = (await session.execute(select(Report).limit(6))).scalars().all()

    with pytest.raises(AssertionError, match="expected at most 2 queries"), assert_max_queries(2):
        for report in reports:
            # BUG: one SELECT per report — this is the N+1, in miniature.
            await session.refresh(report, ["author"])


async def test_list_response_never_exposes_sensitive_columns(
    client: AsyncClient, two_orgs: dict[str, Any]
) -> None:
    """cost_cents and internal_notes exist on every row in the database and must
    not appear on the wire. Phase 2 breaks this on purpose; here it holds."""
    response = await client.get("/reports?limit=3")
    body = response.text
    assert "cost_cents" not in body
    assert "internal_notes" not in body
    assert "INTERNAL" not in body
