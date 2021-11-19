import json
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy import func

from db.initialize_db import Base

class User(Base):
    __tablename__ = "user"

    idx = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    name = Column(
        String(32),
        nullable=False
    )

    register = Column(
        DateTime,
        default=datetime.now(),
        nullable=False
    )

    email = Column(
        String(100),
        nullable=False
    )

    password = Column(
        String(100),
        nullable=False
    )

    server = Column(  # JSON으로 처리하기
        Text,
        nullable=True
    )

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password
        self.server = "undefined"

    def __repr__(self):
        # return '{"id":%d, "name":"%s"}' % (self.idx, self.name)
        return json.dumps({"id": self.idx, "name": self.name})


# class Private(Base):
#     __tablename__ = "private"

#     server = Column(   # 보내는 사람
#         Integer,
#         nullable=False
#     )

#     client = Column(   # 받는 사람
#         Integer,
#         nullable=False
#     )

#     content = Column(
#         Text
#     )

#     fileid = Column(
#         Integer,
#         nullable=False
#     )

#     def __repr__(self):
#         return f"<Private server={self.server}, client={self.client}>"


class Room(Base):
    __tablename__ = "room"

    idx = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    title = Column(
        String(32),
        nullable=False,
        default="New Server"
    )

    create = Column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    owner = Column(
        Integer,
        nullable=False
    )

    def __repr__(self):
        return f"<Room idx={self.idx}, title={self.title!r}>"


class Chat(Base):
    __tablename__ = "chat"

    idx = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    room = Column(
        Integer,
        nullable=False
    )

    author = Column(
        Integer,
        nullable=False,
        unique=True
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=func.now()
    )

    content = Column(
        Text
    )

    def __repr__(self):
        return f"<Chat idx={self.idx}, roon={self.room}>"

class Dm_list(Base):
    __tablename__ = "dm_list"

    name = Column(
        Integer,
        nullable=False,
        unique=True
    )


class Ban(Base):
    __tablename__ = "ban"

    idx = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    user = Column(
        Integer,
        nullable=False
    )

    room = Column(
        Integer,
        nullable=False
    )

    why = Column(
        String(2000),
        nullable=False,
        default="No reason."
    )

    def __repr__(self):
        return f"<Ban idx={self.idx}, user={self.user},room={self.room}>"
