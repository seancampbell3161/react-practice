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


async def test_get_book_returns_one_book(client: AsyncClient) -> None:
    listed = (await client.get("/api/books")).json()[0]
    res = await client.get(f"/api/books/{listed['id']}")
    assert res.status_code == 200
    assert res.json() == listed


async def test_get_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.get("/api/books/nope")
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}


async def test_create_book_returns_201_with_generated_id(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Piranesi", "author": "Susanna Clarke", "status": "reading"})
    assert res.status_code == 201
    body = res.json()
    assert body["id"]
    assert body["title"] == "Piranesi"
    assert body["status"] == "reading"


async def test_created_book_appears_in_list(client: AsyncClient) -> None:
    before = len((await client.get("/api/books")).json())
    created = (await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem"})).json()
    after = (await client.get("/api/books")).json()
    assert len(after) == before + 1
    assert any(b["id"] == created["id"] for b in after)


async def test_create_book_defaults_status_to_want(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem"})
    assert res.status_code == 201
    assert res.json()["status"] == "want"


async def test_create_book_rejects_out_of_range_rating(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"title": "Solaris", "author": "Stanislaw Lem", "rating": 9})
    assert res.status_code == 422


async def test_create_book_ignores_client_supplied_id(client: AsyncClient) -> None:
    res = await client.post("/api/books", json={"id": "hacked", "title": "Solaris", "author": "Stanislaw Lem"})
    assert res.status_code == 201
    assert res.json()["id"] != "hacked"


async def test_update_book_changes_only_provided_fields(client: AsyncClient) -> None:
    original = (await client.get("/api/books")).json()[0]
    res = await client.put(f"/api/books/{original['id']}", json={"status": "read"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "read"
    assert body["title"] == original["title"]
    assert body["author"] == original["author"]
    assert body["rating"] == original["rating"]


async def test_update_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.put("/api/books/nope", json={"status": "read"})
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}


async def test_delete_book_returns_204_and_removes_it(client: AsyncClient) -> None:
    target = (await client.get("/api/books")).json()[0]
    res = await client.delete(f"/api/books/{target['id']}")
    assert res.status_code == 204
    assert res.content == b""
    remaining = (await client.get("/api/books")).json()
    assert all(b["id"] != target["id"] for b in remaining)


async def test_delete_book_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.delete("/api/books/nope")
    assert res.status_code == 404
    assert res.json() == {"detail": "Book not found"}
