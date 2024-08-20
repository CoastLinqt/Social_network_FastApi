import datetime

import pytest
from sqlalchemy import select

from ..conftest import async_session_maker
from ..models import Likes, Media, Tweet, Users


@pytest.mark.asyncio
async def test_add_user_db():
    async with async_session_maker() as session:
        user_1 = Users(name="George", api_key="test")
        user_2 = Users(name="Vitya", api_key="user1")
        session.add_all([user_1, user_2])
        await session.commit()

        query = select(Users.id)
        result = await session.execute(query)

        assert len(result.all()) == 2


@pytest.mark.asyncio
async def test_add_tweet_db():
    async with async_session_maker() as session:
        tweet_1 = Tweet(
            tweet_data="Hello!", create_date=datetime.datetime.now(), author_id=1
        )
        tweet_2 = Tweet(
            tweet_data="Hello world!", create_date=datetime.datetime.now(), author_id=2
        )
        session.add_all([tweet_1, tweet_2])
        await session.commit()

        query = select(Tweet.id)
        result = await session.execute(query)
        assert len(result.all()) == 2


@pytest.mark.asyncio
async def test_add_media_db():
    async with async_session_maker() as session:
        media = Media(file_location="/images/26T8JXnhjP.png", tweet_id=1)
        session.add(media)
        await session.commit()

        query = select(Media.id)
        result = await session.execute(query)
        assert len(result.all()) == 1


@pytest.mark.asyncio
async def test_add_likes_db():
    async with async_session_maker() as session:
        like = Likes(author_id=1, tweet_id=2)
        session.add(like)
        await session.commit()

        query = select(Media.id)
        result = await session.execute(query)
        assert len(result.all()) == 1
