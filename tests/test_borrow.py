from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    response = client.post("/register", json={
        "name": "Test User",
        "email": "testuser123@gmail.com",
        "password": "123456"
    })

    assert response.status_code == 200


def test_login_user():
    response = client.post("/login", json={
        "email": "testuser123@gmail.com",
        "password": "123456"
    })

    assert response.status_code == 200


def test_borrow_book():
    response = client.post("/borrow/1", json={
        "user_id": 1
    })

    assert response.status_code == 200


def test_borrow_history():
    response = client.get("/borrow/history/1")
    assert response.status_code == 200


def test_return_book():
    response = client.post("/return/1", json={
        "user_id": 1
    })

    assert response.status_code == 200