from typing import List, Optional

from pydantic import BaseModel, Field


class ResponseTrue(BaseModel):
    result: str = Field(default="true")


class TweetRequest(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = list()


class Author(BaseModel):
    id: int
    name: str


class Likes(BaseModel):
    user_id: int
    name: str


class Tweets(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: Author
    likes: List[Likes]


class Forbidden(BaseModel):
    detail: str = Field(default="Sorry, you can't delete another user's tweets.")


class MediaResponse(BaseModel):
    result: str = Field(default="true")
    media_id: int


class TweetResponsePost(BaseModel):
    result: str = Field(default="true")
    tweet_id: int


class TweetResponseGet(BaseModel):
    result: str = Field(default="true")
    tweets: List[Tweets]


class User(BaseModel):
    id: int
    name: str
    followers: List[Author]
    following: List[Author]


class UsersGet(BaseModel):
    result: str = Field(default="true")
    user: User


class ErrorResponse(BaseModel):
    result: str = Field(default="false")
    error_type: str
    error_message: str


class BadRequest(BaseModel):
    detail: str = "You can't sign yourself"
