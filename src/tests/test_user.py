import pytest
from httpx import AsyncClient

ERROR_TYPE = {
    "error_message": "User was not found",
    "error_type": "UserNotFound",
    "result": "false",
}

BAD_REQUEST = {"detail": "You can't sign yourself"}


@pytest.mark.asyncio
async def test_users_me(ac: AsyncClient):

    response = await ac.get("api/users/me", headers=({"api-key": "user2"}))

    assert response.status_code == 200
    assert response.json()["result"] == "true"


@pytest.mark.asyncio
async def test_users_not_found(ac: AsyncClient):

    response = await ac.get(f"api/users/{422}")

    assert response.status_code == 404
    assert response.json() == ERROR_TYPE


@pytest.mark.asyncio
async def test_users_following(ac: AsyncClient):

    response = await ac.post(f"api/users/{1}/follow", headers=({"api-key": "user2"}))

    assert response.status_code == 200
    assert response.json()["result"] == "true"


@pytest.mark.asyncio
async def test_yourself_following(ac: AsyncClient):

    response = await ac.post(f"api/users/{1}/follow", headers=({"api-key": "test"}))

    assert response.status_code == 400
    assert response.json() == BAD_REQUEST


@pytest.mark.asyncio
async def test_following_not_found(ac: AsyncClient):

    response = await ac.post(f"api/users/{524}/follow", headers=({"api-key": "user2"}))

    assert response.status_code == 404

    assert response.json() == ERROR_TYPE


@pytest.mark.asyncio
async def test_users_unfollowing(ac: AsyncClient):

    response = await ac.delete(f"api/users/{1}/follow", headers=({"api-key": "user2"}))

    assert response.status_code == 200

    assert response.json()["result"] == "true"


@pytest.mark.asyncio
async def test_unfollowing_not_found(ac: AsyncClient):

    response = await ac.delete(
        f"api/users/{500}/follow", headers=({"api-key": "user2"})
    )

    assert response.status_code == 404

    assert response.json() == ERROR_TYPE
