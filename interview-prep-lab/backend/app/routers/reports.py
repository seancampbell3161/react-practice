"""Report reads.

Phase 0 ships one honest, correct list endpoint. Phase 1 parks the paired
`/reports/n-plus-one` vs `/reports/selectin` variants next to it so you can diff
the X-Query-Count header between them.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Report
from app.schemas import ReportListItem

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportListItem])
async def list_reports(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 25,
) -> list[ReportListItem]:
    stmt = (
        select(Report)
        .options(selectinload(Report.author))
        .order_by(Report.created_at.desc(), Report.id.desc())
        .limit(limit)
    )
    reports = (await session.execute(stmt)).scalars().all()
    return [
        ReportListItem(
            id=r.id,
            org_id=r.org_id,
            author_id=r.author_id,
            title=r.title,
            body=r.body,
            status=r.status,
            created_at=r.created_at,
            author_email=r.author.email,
        )
        for r in reports
    ]
