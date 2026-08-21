"""Seed the lab.

    uv run python -m app.seed                 # small, comfortable dataset
    uv run python -m app.seed --reports 50000 # the dataset that makes it hurt

The big seed is the point. N+1, deep offset pagination, and "just call .all()"
are all perfectly pleasant at 20 rows; they only teach at 50k.

Everything here is deterministic — fixed RNG seed, fixed base timestamp — so the
row counts and page boundaries you quote in one session are the same in the next.
"""

from __future__ import annotations

import argparse
import asyncio
import random
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models import Org, Report, User

# A fixed point in time so created_at values are reproducible run to run.
EPOCH = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

ORG_SPECS = [
    ("Acme Corp", "acme"),
    ("Globex", "globex"),
]
FIRST_NAMES = ["ada", "brice", "cleo", "dev", "esme"]

# TODO(interview-prep): Phase 7 replaces this with a real argon2 hash and gives
# every seeded user the password "password". Until then nothing verifies it.
PLACEHOLDER_HASH = "unhashed$placeholder"

STATUSES = ["draft", "draft", "submitted", "approved"]

# How many reports share one exact created_at, to prove the keyset cursor's
# (created_at, id) tiebreaker in Phase 6 neither skips nor repeats them.
TIE_CLUSTER = 5


async def seed(report_count: int, batch_size: int = 5_000) -> None:
    rng = random.Random(1337)

    async with SessionLocal() as session:
        # Orgs cascade to users and reports, so one delete clears everything.
        await session.execute(delete(Org))
        await session.commit()

        orgs = [Org(id=uuid.uuid4(), name=name) for name, _ in ORG_SPECS]
        session.add_all(orgs)
        await session.flush()

        users: list[User] = []
        for org, (_, slug) in zip(orgs, ORG_SPECS, strict=True):
            for i, first in enumerate(FIRST_NAMES):
                users.append(
                    User(
                        id=uuid.uuid4(),
                        org_id=org.id,
                        email=f"{first}@{slug}.test",
                        hashed_password=PLACEHOLDER_HASH,
                        role="admin" if i == 0 else "member",
                    )
                )
        session.add_all(users)
        await session.commit()

        by_org: dict[uuid.UUID, list[User]] = {org.id: [] for org in orgs}
        for user in users:
            by_org[user.org_id].append(user)

        rows: list[dict[str, object]] = []
        written = 0
        for i in range(report_count):
            org = orgs[i % len(orgs)]
            author = rng.choice(by_org[org.id])

            # The last TIE_CLUSTER rows all land on the same second.
            if i >= report_count - TIE_CLUSTER:
                created_at = EPOCH + timedelta(minutes=report_count)
            else:
                created_at = EPOCH + timedelta(minutes=i)

            rows.append(
                {
                    "id": uuid.uuid4(),
                    "org_id": org.id,
                    "author_id": author.id,
                    "title": f"Report #{i + 1:06d} — {org.name}",
                    "body": f"Findings for period {i + 1}. " * rng.randint(2, 8),
                    "status": rng.choice(STATUSES),
                    # Sensitive on purpose. If either of these ever shows up in a
                    # client response, that is the bug the lab is teaching.
                    "cost_cents": rng.randint(500, 500_000),
                    "internal_notes": f"INTERNAL: margin note for report {i + 1}",
                    "created_at": created_at,
                }
            )

            if len(rows) >= batch_size:
                await session.execute(insert(Report), rows)
                await session.commit()
                written += len(rows)
                rows.clear()
                print(f"  ... {written:,}/{report_count:,} reports")

        if rows:
            await session.execute(insert(Report), rows)
            await session.commit()
            written += len(rows)

        await _print_summary(session, written)


async def _print_summary(session: AsyncSession, written: int) -> None:
    print(f"\nSeeded {written:,} reports across {len(ORG_SPECS)} orgs.\n")
    orgs = (await session.execute(select(Org).order_by(Org.name))).scalars().all()
    for org in orgs:
        members = (
            (await session.execute(select(User).where(User.org_id == org.id).order_by(User.email)))
            .scalars()
            .all()
        )
        print(f"  {org.name}  id={org.id}")
        for user in members:
            print(f"    {user.role:<6} {user.email:<22} id={user.id}")
        sample = (
            await session.execute(
                select(Report.id)
                .where(Report.org_id == org.id)
                .order_by(Report.created_at)
                .limit(1)
            )
        ).scalar_one_or_none()
        print(f"    sample report id: {sample}\n")
    print("Cross-org tip: authenticate as an Acme user, then request a Globex")
    print("report id. Phase 3 is where that stops working.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the interview prep lab database.")
    parser.add_argument(
        "--reports",
        type=int,
        default=20,
        help="How many reports to create (default: 20; try 50000).",
    )
    args = parser.parse_args()

    async def _run() -> None:
        try:
            await seed(args.reports)
        finally:
            await engine.dispose()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
