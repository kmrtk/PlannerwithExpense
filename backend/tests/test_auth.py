from tests.conftest import register_user


def test_register_returns_access_token(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "password123", "name": "Alice"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_registered_user_succeeds(client):
    register_user(client, "bob@example.com", password="password123")

    response = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_register_with_duplicate_email_fails(client):
    register_user(client, "carol@example.com")

    response = client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "another-password"},
    )
    assert response.status_code == 400


def test_login_with_wrong_password_fails(client):
    register_user(client, "dave@example.com", password="correct-password")

    response = client.post(
        "/api/auth/login",
        json={"email": "dave@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
