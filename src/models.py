from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import DeclarativeBase, relationship

from database import engine  # type: ignore


class Model(DeclarativeBase):
    pass


followers = Table(
    "followers",
    Model.metadata,
    Column("follower_id", Integer, ForeignKey("users.id")),
    Column("following_id", Integer, ForeignKey("users.id")),
)


class Media(Model):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_location = Column(String, nullable=False)
    tweet_id = Column(
        Integer, ForeignKey("tweet.id", ondelete="CASCADE"), autoincrement=True
    )


class Likes(Model):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    tweet_id = Column(Integer, ForeignKey("tweet.id", ondelete="CASCADE"))


class Users(Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)

    follower = relationship(
        "Users",
        secondary=followers,
        primaryjoin=(followers.c.following_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        backref="following",
        lazy="selectin",
    )

    api_key = Column(String(), nullable=None)

    def __repr__(self):
        return f"id={self.id}," f" name={self.name}"


class Tweet(Model):
    __tablename__ = "tweet"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_data = Column(String(3000))
    create_date = Column(DateTime, server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    media = relationship(
        "Media", backref="tweet", cascade="all, delete", lazy="selectin"
    )

    tweet_author_id = relationship(
        "Users", backref="tweet", cascade="all, delete", lazy="selectin"
    )

    likes = relationship(
        "Likes", backref="tweet", cascade="all, delete", lazy="selectin"
    )

    def __repr__(self):
        return f"id={self.id}," f" tweet_data={self.tweet_data}"


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
