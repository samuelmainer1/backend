from fastapi.testclient import TestClient

from tests.conftest import get_test_client

client = get_test_client()


def _unique_suffix() -> str:
    import time

    return str(int(time.time() * 1000))


def _signup_and_login(suffix: str) -> str:
    email = f"test_{suffix}@example.com"
    username = f"tester_{suffix}"

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "secret123"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["username"] == username
    assert data["email"] == email

    resp3 = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "secret123"},
    )
    assert resp3.status_code == 200, resp3.text
    token_data = resp3.json()
    assert "access_token" in token_data
    return token_data["access_token"]


def test_register_and_login():
    _signup_and_login(_unique_suffix())


def test_duplicate_register_conflicts():
    suffix = _unique_suffix()
    email = f"dup_{suffix}@example.com"
    username = f"duper_{suffix}"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "secret123"},
    )
    resp2 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "secret123"},
    )
    assert resp2.status_code == 409


def test_protected_route():
    token = _signup_and_login(_unique_suffix())
    resp = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["is_active"] is True


def test_wrong_password_rejected():
    suffix = _unique_suffix()
    username = f"wrongpw_{suffix}"
    client.post(
        "/api/v1/auth/register",
        json={"email": f"wrongpw_{suffix}@example.com", "username": username, "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "wrongpassword"},
    )
    assert resp.status_code == 401