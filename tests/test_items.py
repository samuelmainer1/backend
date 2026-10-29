from fastapi.testclient import TestClient

from tests.conftest import get_test_client

client = get_test_client()


def _unique_suffix() -> str:
    import time

    return str(int(time.time() * 1000))


def _get_token():
    suffix = _unique_suffix()
    email = f"item_{suffix}@example.com"
    username = f"itemuser_{suffix}"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "secret123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_create_and_list_items():
    token = _get_token()
    resp = client.post(
        "/api/v1/items/",
        json={"title": "Test Item", "description": "A test item"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    item = resp.json()
    assert item["title"] == "Test Item"

    resp2 = client.get("/api/v1/items/", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200
    assert len(resp2.json()) >= 1