from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_add_book():
    response = client.post("/books", json={
        "title": "Test Book",
        "author": "Author",
        "category": "Test",
        "total_copies": 2
    })

    assert response.status_code == 200
    assert response.json()["book"]["title"] == "Test Book"


def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert "books" in response.json()


def test_search_books():
    response = client.get("/books/search?query=test")
    assert response.status_code == 200


def test_overdue_books():
    response = client.get("/books/overdue")
    assert response.status_code == 200
    assert "overdue_books" in response.json()