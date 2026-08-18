from operator import indexOf
import uuid

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from app.data import BOOKS
from app.models import Book, BookCreate, BookUpdate

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


#   GET    /{book_id}   -> 200 Book, or 404
@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str) -> Book:
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )

    
#   POST   ""           -> 201 Book, id generated server-side
@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(req: BookCreate) -> Book:
    if req.rating and  req.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Rating of {req.rating} is not valid"
        )
    new_book = Book(id=uuid.uuid4().hex, title=req.title, author=req.author, status=req.status, rating=req.rating)

    BOOKS.append(new_book)

    return new_book
#   PUT    /{book_id}   -> 200 Book, applying only the fields that were sent
@router.put("/{book_id}", response_model=Book)
async def update_book(book_id: str, req: BookUpdate) -> Book:
    book = None
    idx = -1

    for i, b in enumerate(BOOKS):
        if b.id == book_id:
            book = b
            idx = i

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    update_data = req.model_dump(exclude_unset=True, exclude_none=False)
    BOOKS[idx] = book.model_copy(update=update_data)

    return BOOKS[idx]
        
#   DELETE /{book_id}   -> 204 with an empty body, or 404
