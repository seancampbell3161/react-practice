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


class BookCreate(BaseModel):
    title: str
    author: str
    status: BookStatus = BookStatus.WANT
    rating: int | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    status: BookStatus | None = None
    rating: int | None = None