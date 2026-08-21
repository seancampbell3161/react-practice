"""Pydantic v2 models — the wire contract, kept separate from the ORM models.

Phase 2 grows this file into the full three-model family (ReportCreate /
ReportOut / SQLAlchemy Report) and adds the deliberately-unsafe variants.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportOut(BaseModel):
    """What a client is allowed to see.

    Note what is *absent*: `cost_cents` and `internal_notes`. Omission is the
    whole point — this schema is the boundary that stops them leaking.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    author_id: uuid.UUID
    title: str
    body: str
    status: str
    created_at: datetime


class ReportListItem(ReportOut):
    """List rows carry the author's email, which is what makes N+1 visible."""

    author_email: str
