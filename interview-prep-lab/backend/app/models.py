"""The whole domain: org -> users -> reports.

Multi-tenant on purpose. Two orgs is what makes the authorization exercises real
rather than hypothetical: every read has to answer "whose row is this?".
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

ROLES = ("member", "admin")
REPORT_STATUSES = ("draft", "submitted", "approved")


class Base(DeclarativeBase):
    pass


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    users: Mapped[list[User]] = relationship(back_populates="org", cascade="all, delete-orphan")
    reports: Mapped[list[Report]] = relationship(back_populates="org", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")

    org: Mapped[Org] = relationship(back_populates="users")
    reports: Mapped[list[Report]] = relationship(back_populates="author")

    __table_args__ = (CheckConstraint("role IN ('member', 'admin')", name="ck_users_role"),)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")

    # These two are the "must never reach the client" fields. Phase 2 leaks them
    # on purpose through a response_model-less endpoint, then fixes it.
    cost_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    internal_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # lazy="select" is the SQLAlchemy default and we are keeping it: it is the
    # mechanism behind the Phase 1 N+1 demo. Touching `report.author` in a loop
    # fires one SELECT per row, which is precisely the lesson.
    org: Mapped[Org] = relationship(back_populates="reports")
    author: Mapped[User] = relationship(back_populates="reports")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'submitted', 'approved')", name="ck_reports_status"),
        # The keyset-pagination index for Phase 6. (created_at, id) is also the
        # cursor's sort key — the id is the tiebreaker that stops rows sharing a
        # created_at from being skipped or repeated across pages.
        Index("ix_reports_created_at_id", "created_at", "id"),
    )
