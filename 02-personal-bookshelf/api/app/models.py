from enum import Enum

from pydantic import BaseModel


class BookStatus(str, Enum):
    WANT = "want"
    READING = "reading"
    READ = "read"


class Book(BaseModel):
    """The shape every endpoint returns. The frontend is specced against this."""

    id: str
    title: str
    author: str
    status: BookStatus
    rating: int | None = None


# Define BookCreate (the POST body) and BookUpdate (the PUT body) here.
class BookCreate(BaseModel):
    title: str
    author: str
    status: BookStatus = BookStatus.WANT
    rating: int | None = None
# README.md Part 1 has the field rules; tests/test_books.py has the behavior
# they must satisfy. Both are pydantic models, like Book above.
