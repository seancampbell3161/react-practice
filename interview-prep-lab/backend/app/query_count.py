"""Counts the SQL statements issued inside a request or a test block.

This is the single most load-bearing piece of infrastructure in the lab. It is
what turns "selectinload avoids N+1" from a claim into a number you can read off
a response header (``X-Query-Count``) or assert on in a test
(``assert_max_queries(2)``).

How it works
------------
SQLAlchemy emits ``after_cursor_execute`` once per statement handed to the DBAPI
cursor. We listen for that and bump a counter stashed in a :class:`ContextVar`,
so concurrent requests each get their own tally.

One subtlety worth understanding, because it is exactly the kind of thing an
interviewer can probe: with the *async* engine, the listener does not run in your
coroutine. SQLAlchemy drives the sync DBAPI layer inside a greenlet, and the
listener fires there. That is why the ContextVar holds a **mutable counter
object** that the listener mutates in place, rather than the listener calling
``ContextVar.set()``. Reading a ContextVar across the greenlet boundary is
reliable; writing one is not.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass
class QueryCounter:
    """A per-request / per-test tally of executed statements."""

    count: int = 0
    statements: list[str] = field(default_factory=list)

    def record(self, statement: str) -> None:
        self.count += 1
        # Keep a bounded sample so a runaway N+1 does not eat memory while you
        # are staring at it.
        if len(self.statements) < 200:
            self.statements.append(" ".join(statement.split()))


_current: ContextVar[QueryCounter | None] = ContextVar("lab_query_counter", default=None)

# Transaction bookkeeping is not query load, and counting it would make every
# budget in this lab environment-dependent: the test harness nests each test in a
# SAVEPOINT, so /health would read 1 in dev and 2 under pytest. Excluding these
# keeps one number meaning one thing everywhere.
_TRANSACTION_CONTROL = (
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE SAVEPOINT",
    "ROLLBACK TO SAVEPOINT",
)


def _is_transaction_control(statement: str) -> bool:
    return statement.lstrip().upper().startswith(_TRANSACTION_CONTROL)


def current_counter() -> QueryCounter | None:
    """The counter for the active request/test block, if one is installed."""
    return _current.get()


@contextmanager
def count_queries(*, reuse: bool = False) -> Iterator[QueryCounter]:
    """Install a fresh counter for the duration of the block.

    ``reuse=True`` yields the counter already in scope instead of shadowing it.
    The middleware uses that: in the running app nothing is in scope so it gets
    a fresh counter, but under ``assert_max_queries(n)`` in a test it joins the
    test's counter — so the header the test reads and the number the test
    asserts on are guaranteed to be the same number.
    """
    existing = _current.get()
    if reuse and existing is not None:
        yield existing
        return

    counter = QueryCounter()
    token = _current.set(counter)
    try:
        yield counter
    finally:
        _current.reset(token)


def _after_cursor_execute(
    conn: Any,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: Any,
    executemany: bool,
) -> None:
    counter = _current.get()
    if counter is not None and not _is_transaction_control(statement):
        counter.record(statement)


def install_query_counter(engine: AsyncEngine | Engine) -> None:
    """Attach the listener to an engine (async engines listen on .sync_engine)."""
    target = engine.sync_engine if isinstance(engine, AsyncEngine) else engine
    if not event.contains(target, "after_cursor_execute", _after_cursor_execute):
        event.listen(target, "after_cursor_execute", _after_cursor_execute)
