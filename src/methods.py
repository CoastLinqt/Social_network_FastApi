import os
import random
import shutil

from faker import Faker
from fastapi import Depends, Header, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_async_session
from models import Media, Users

fake_name = Faker()
LENGTH = 10

valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


async def generate_filename():
    return "".join(random.choice(valid_chars) for _ in range(LENGTH))


async def create_upload_file(upload_file: UploadFile):
    directory = os.path.abspath("images")
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_location = f"/images/{await generate_filename()}.png"
    with open(
        file_location,
        "wb",
    ) as file_object:
        shutil.copyfileobj(upload_file.file, file_object)

    return file_location


async def get_user_by_api_key(
    api_key: str, session: AsyncSession = Depends(get_async_session)
):

    users_find = await session.execute(
        select(Users)
        .where(Users.api_key == api_key)
        .options(selectinload(Users.follower), selectinload(Users.following))  # type: ignore
    )
    user = users_find.scalar()

    return user


async def get_user_by_id(id: int, session):
    users_find = await session.execute(
        select(Users)
        .where(Users.id == id)
        .options(selectinload(Users.follower), selectinload(Users.following))  # type: ignore
    )
    user = users_find.scalar()

    return user


async def authenticate_user(
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):

    user_auth = await session.execute(select(Users).where(Users.api_key == api_key))

    if user_auth.scalar() is None:
        new_user = Users(name=fake_name.name(), api_key=api_key)
        session.add(new_user)
        await session.commit()

        user_new = await get_user_by_api_key(api_key=new_user.api_key, session=session)  # type: ignore

        return user_new

    user = await get_user_by_api_key(api_key=api_key, session=session)

    return user


async def get_user_names(current_user):

    user_dict = dict()

    user_dict["id"] = current_user.id
    user_dict["name"] = current_user.name

    followers = current_user.follower

    follower_dict = dict()
    followers_list = list()
    for follower in followers:
        follower_dict["id"] = follower.id
        follower_dict["name"] = follower.name
        followers_list.append(follower_dict)

    user_dict["followers"] = followers_list

    followings = current_user.following
    following_dict = dict()
    following_list = list()
    for following in followings:

        following_dict["id"] = following.id
        following_dict["name"] = following.name
        following_list.append(following_dict)

    user_dict["following"] = following_list

    data = dict()

    data["result"] = "true"
    data["user"] = user_dict

    return data


async def add_media_tweet_id(tweet_in, session, create_tweet):
    stmt = await session.execute(
        select(Media).where(Media.id.in_(tweet_in.tweet_media_ids))
    )
    objects_media = stmt.scalars()

    for media in objects_media:
        if not media.tweet_id:
            media.tweet_id = create_tweet.id
    session.add_all(objects_media)
    await session.commit()


async def data_dict_create_tweet(tweet_id, session):
    data = {}
    tweet_list = list()
    for tweets in tweet_id:
        specific_tweet = dict()
        specific_author = dict()

        specific_tweet["id"] = tweets.id
        specific_tweet["content"] = tweets.tweet_data
        specific_tweet["attachments"] = [
            media_pic.file_location for media_pic in tweets.media
        ]

        specific_author["id"] = tweets.tweet_author_id.id
        specific_author["name"] = tweets.tweet_author_id.name

        specific_tweet["author"] = specific_author
        specific_tweet["likes"] = [
            {
                "user_id": like.author_id,
                "name": await get_name_author(
                    author_id=like.author_id, session=session
                ),
            }
            for like in tweets.likes
        ]
        tweet_list.append(specific_tweet)

    data["result"] = "true"
    data["tweets"] = tweet_list

    return data


async def get_name_author(author_id: int, session):

    user = await session.execute(select(Users.name).where(Users.id == author_id))
    find_user = user.scalar()

    return str(find_user)


async def errors_response(error_type, error_message, tweet_id=""):
    if tweet_id is None:
        return {
            "result": "false",
            "error_type": "TweetNotFound",
            "error_message": "Please check tweet details for availability",
        }

    return {
        "result": "false",
        "error_type": f"{error_type}",
        "error_message": f"{error_message}",
    }
