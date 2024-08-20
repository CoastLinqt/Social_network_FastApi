from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_async_session
from methods import (
    add_media_tweet_id,
    authenticate_user,
    create_upload_file,
    data_dict_create_tweet,
    errors_response,
    get_user_by_api_key,
    get_user_by_id,
    get_user_names,
)
from models import Likes, Media, Tweet, Users
from schemas import (
    BadRequest,
    ErrorResponse,
    Forbidden,
    MediaResponse,
    ResponseTrue,
    TweetRequest,
    TweetResponseGet,
    TweetResponsePost,
    UsersGet,
)

router = APIRouter(prefix="/api")


@router.post("/medias", response_model=MediaResponse)
async def post_media(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)
):

    new_file = await create_upload_file(file)
    new_media = Media(file_location=new_file)
    session.add(new_media)
    await session.commit()

    return {"result": "true", "media_id": new_media.id}


@router.post(
    "/tweets",
    responses={404: {"model": ErrorResponse}, 200: {"model": TweetResponsePost}},
)
async def post_tweet(
    tweet_in: TweetRequest,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):

    find_user = await session.execute(select(Users.id).filter(Users.api_key == api_key))
    if find_user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound", error_message="User was not found"
            ),
        )

    create_tweet = Tweet(tweet_data=tweet_in.tweet_data, author_id=find_user.scalar())
    session.add(create_tweet)

    await session.commit()

    await add_media_tweet_id(
        tweet_in=tweet_in, session=session, create_tweet=create_tweet
    )

    return {"result": "true", "tweet_id": create_tweet.id}


@router.get("/tweets", response_model=TweetResponseGet)
async def get_tweet(session: AsyncSession = Depends(get_async_session)):

    tweet = await session.execute(
        select(Tweet)
        .options(
            selectinload(Tweet.media),
            selectinload(Tweet.tweet_author_id),
            selectinload(Tweet.likes),
        )
        .order_by(desc(Tweet.id))
    )

    tweet_id = tweet.scalars()

    result = await data_dict_create_tweet(tweet_id=tweet_id, session=session)

    return result


@router.get("/users/me", response_model=UsersGet)
async def get_user(
    current_user=Depends(authenticate_user),
):
    data = await get_user_names(current_user=current_user)

    return data


@router.get(
    "/users/{id}", responses={404: {"model": ErrorResponse}, 200: {"model": UsersGet}}
)
async def specific_users(id: int, session: AsyncSession = Depends(get_async_session)):
    specific_user = await get_user_by_id(id=id, session=session)
    if specific_user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound", error_message="User was not found"
            ),
        )

    data = await get_user_names(current_user=specific_user)

    return data


@router.delete(
    "/tweets/{tweet_id}",
    responses={
        200: {"model": ResponseTrue},
        403: {"model": Forbidden},
        404: {"model": ErrorResponse},
    },
)
async def delete_tweet(
    tweet_id: int,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):

    user = await session.execute(select(Users.id).filter(Users.api_key == api_key))
    user_find = user.scalar()
    author_tweet = await session.execute(
        select(Tweet.author_id).where(Tweet.id == tweet_id)
    )
    author_id_find = author_tweet.scalar()

    if not user_find or not author_id_find:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound",
                error_message="User was not found",
                tweet_id=author_id_find,
            ),
        )

    if user_find != author_id_find:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sorry, you can't delete another user's tweets.",
        )

    await session.execute(delete(Tweet).where(Tweet.id == tweet_id))
    await session.commit()

    return {"result": "true"}


@router.post(
    "/tweets/{id}/likes",
    responses={404: {"model": ErrorResponse}, 200: {"model": ResponseTrue}},
)
async def user_put_like(
    id: int,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):

    user = await session.execute(select(Users.id).filter(Users.api_key == api_key))
    tweet = await session.execute(select(Tweet.id).where(Tweet.id == id))
    tweet_find = tweet.scalar()
    user_find = user.scalar()

    if not user_find or not tweet_find:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound",
                error_message="User was not found",
                tweet_id=tweet_find,
            ),
        )

    likes = await session.execute(
        select(func.count(Likes.id)).filter(
            Likes.author_id == user_find, Likes.tweet_id == tweet_find
        )
    )

    likes_result = likes.scalar()
    if likes_result == 0:

        likes_add = Likes(author_id=user_find, tweet_id=tweet_find)
        session.add(likes_add)
        await session.commit()

        return {"result": "true"}


@router.delete(
    "/tweets/{id}/likes",
    responses={404: {"model": ErrorResponse}, 200: {"model": ResponseTrue}},
)
async def delete_like(
    id: int,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):

    user = await session.execute(select(Users.id).filter(Users.api_key == api_key))
    tweet = await session.execute(select(Tweet.id).where(Tweet.id == id))
    user_find = user.scalar()
    tweet_find = tweet.scalar()

    if not user_find or not tweet_find:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound",
                error_message="User was not found",
                tweet_id=tweet_find,
            ),
        )

    likes_id = await session.execute(
        select(Likes.id).where(
            Likes.author_id == user_find, Likes.tweet_id == tweet_find
        )
    )
    result_id = likes_id.scalar()

    await session.execute(delete(Likes).where(Likes.id == result_id))
    await session.commit()

    return {"result": "true"}


@router.post(
    "/users/{id}/follow",
    responses={
        404: {"model": ErrorResponse},
        400: {"model": BadRequest},
        200: {"model": ResponseTrue},
    },
)
async def tweet_subscribe(
    id: int,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):
    follower_user = await get_user_by_id(id=id, session=session)

    user_following = await get_user_by_api_key(api_key=api_key, session=session)

    if follower_user == user_following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can't sign yourself"
        )

    if not follower_user or not user_following:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound",
                error_message="User was not found",
            ),
        )

    follower_user.follower.append(user_following)

    await session.commit()

    return {"result": "true"}


@router.delete(
    "/users/{id}/follow",
    responses={404: {"model": ErrorResponse}, 200: {"model": ResponseTrue}},
)
async def delete_subscribe(
    id: int,
    api_key: str = Header(None),
    session: AsyncSession = Depends(get_async_session),
):
    follower_user = await get_user_by_id(id=id, session=session)

    user_following = await get_user_by_api_key(api_key=api_key, session=session)

    if not follower_user or not user_following:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=await errors_response(
                error_type="UserNotFound", error_message="User was not found"
            ),
        )

    follower_user.follower.remove(user_following)

    await session.commit()

    return {"result": "true"}
