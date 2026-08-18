from httpx import AsyncClient

from app.data import SEED


async def test_list_books_returns_seeded_books(client: AsyncClient) -> None:
    res = await client.get("/api/books")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)
    assert len(body) == len(SEED)
    assert set(body[0]) == {"id", "title", "author", "status", "rating"}


async def test_store_is_reset_between_tests(client: AsyncClient) -> None:
    body = (await client.get("/api/books")).json()
    assert len(body) == len(SEED)
