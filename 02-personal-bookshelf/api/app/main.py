from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.books import router as books_router

app = FastAPI(title="Personal Bookshelf API")

# The frontend runs on http://localhost:5173, a different origin, so the
# browser needs CORS headers to let it call this API. Wide open is fine for
# local practice; a real service would name its allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router, prefix="/api/books")
