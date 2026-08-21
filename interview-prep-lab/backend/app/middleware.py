"""ASGI middleware that stamps every response with its SQL query count."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from starlette.datastructures import MutableHeaders

from app.query_count import count_queries

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class QueryCountMiddleware:
    """Adds ``X-Query-Count`` to every HTTP response.

    Deliberately written as raw ASGI rather than ``BaseHTTPMiddleware``: raw ASGI
    middleware runs in the *same* task as the endpoint, so the ContextVar the
    counter lives in is unambiguously the one the endpoint sees.
    ``BaseHTTPMiddleware`` spawns the endpoint in a child task, which copies the
    context — it happens to work here, but "happens to work" is not what you want
    from the instrument you are using to measure everything else.
    """

    def __init__(self, app: Callable[[Scope, Receive, Send], Awaitable[None]]) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        with count_queries(reuse=True) as counter:

            async def send_with_header(message: Message) -> None:
                if message["type"] == "http.response.start":
                    MutableHeaders(scope=message)["X-Query-Count"] = str(counter.count)
                await send(message)

            await self.app(scope, receive, send_with_header)
