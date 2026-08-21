"""Liveness plus a cheap DB round-trip, so /health also proves connectivity."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(session: Annotated[AsyncSession, Depends(get_session)]) -> dict[str, Any]:
    # One statement — so a fresh /health is also the simplest possible check
    # that the X-Query-Count header is wired up. It should read exactly 1.
    result = await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": result.scalar_one() == 1}
