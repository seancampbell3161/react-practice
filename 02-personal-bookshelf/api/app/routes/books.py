from fastapi import APIRouter

from app.data import BOOKS
from app.models import Book

router = APIRouter()


@router.get("", response_model=list[Book])
async def list_books() -> list[Book]:
    """Return every book in the store.

    The worked example. Note the three pieces you will reuse below: the
    decorator naming the method and path (relative to the /api/books prefix
    set in main.py), `response_model` telling FastAPI the shape to serialize
    and document, and `async def`.
    """
    return BOOKS


# --- Your turn --------------------------------------------------------------
# Implement the other four endpoints:
#
#   GET    /{book_id}   -> 200 Book, or 404
#   POST   ""           -> 201 Book, id generated server-side
#   PUT    /{book_id}   -> 200 Book, applying only the fields that were sent
#   DELETE /{book_id}   -> 204 with an empty body, or 404
#
# README.md Part 1 has the full contract. tests/test_books.py is the spec -
# run `uv run pytest` and work until it is green.
