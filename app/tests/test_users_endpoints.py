import pytest
from httpx import AsyncClient

from .factories import UserPayloadFactory


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):

    payload = UserPayloadFactory()
    response = await client.post("/users/", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_users_list(client: AsyncClient):

    # створюємо юзера
    payload = UserPayloadFactory()
    create_resp = await client.post("/users/", json=payload)
    assert create_resp.status_code == 200

    # отримуємо список
    response = await client.get("/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    # шукаємо нашого юзера по email
    emails = [u["email"] for u in data]
    assert payload["email"] in emails


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):

    # Спочатку створимо юзера
    payload = UserPayloadFactory()
    create_resp = await client.post("/users/", json=payload)
    assert create_resp.status_code == 200
    user_id = create_resp.json()["id"]

    # Видаляємо
    delete_resp = await client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"

    # Перевіряємо, що його більше немає у списку
    list_resp = await client.get("/users/")
    assert list_resp.status_code == 200
    users = list_resp.json()
    ids = [u["id"] for u in users]
    assert user_id not in ids


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client: AsyncClient):

    response = await client.delete("/users/non-existent-id-123")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"
