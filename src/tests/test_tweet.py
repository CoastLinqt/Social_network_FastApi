import os.path
from io import BytesIO

import pytest
from httpx import AsyncClient

FORBIDDEN_ERROR = {"detail": "Sorry, you can't delete another user's tweets."}
TWEET_NOT_FOUND = {
    "result": "false",
    "error_type": "TweetNotFound",
    "error_message": "Please check tweet details for availability",
}


@pytest.mark.asyncio
async def test_tweet_integer(ac: AsyncClient):
    response = await ac.post(
        "api/tweets",
        json={"tweet_data": 1, "tweet_media_ids": [1]},
        headers=({"api-key": "test"}),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tweet_get(ac: AsyncClient):
    response = await ac.get(
        "api/tweets",
        headers=({"api-key": "test"}),
    )
    assert response.json()["result"] == "true"
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_tweet_delete_yourself(ac: AsyncClient):
    response = await ac.delete(
        f"api/tweets/{2}",
        headers=({"api-key": "test"}),
    )
    assert response.json() == FORBIDDEN_ERROR
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tweet_delete_not_found(ac: AsyncClient):
    response = await ac.delete(
        f"api/tweets/{500}",
        headers=({"api-key": "test"}),
    )
    assert response.json() == TWEET_NOT_FOUND
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tweet_delete_string(ac: AsyncClient):
    response = await ac.delete(
        f"api/tweets/{'Hello'}",
        headers=({"api-key": "test"}),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tweet_likes(ac: AsyncClient):
    response = await ac.post(
        f"api/tweets/{3}/likes",
        headers=({"api-key": "test"}),
    )
    assert response.json()["result"] == "false"
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tweet_likes_complete(ac: AsyncClient):
    response = await ac.post(
        f"api/tweets/{1}/likes",
        headers=({"api-key": "test"}),
    )

    assert response.json()["result"] == "true"
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_tweet_likes_delete(ac: AsyncClient):
    response = await ac.delete(
        f"api/tweets/{3}/likes",
        headers=({"api-key": "test"}),
    )
    assert response.json()["result"] == "false"
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_likes_delete_complete(ac: AsyncClient):
    response = await ac.delete(
        f"api/tweets/{1}/likes",
        headers=({"api-key": "test"}),
    )

    assert response.json()["result"] == "true"
    assert response.status_code == 200
