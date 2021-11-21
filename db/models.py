from datetime import datetime

from sqlalchemy import func

from web import db


class Counter(db.Model):
    __bind_key__ = "main"
    __table_args__ = {'extend_existing': True}

    count = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )


class User(db.Model):
    __bind_key__ = "main"
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Text,
        unique=True,
        primary_key=True,
        nullable=False
    )

    name = db.Column(
        db.String(32),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.now(),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    server = db.Column(  # JSON 으로 처리하기
        db.Text,
        nullable=True
    )


class Room(db.Model):
    __bind_key__ = "main"
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Text,
        unique=True,
        primary_key=True,
        nullable=False
    )

    title = db.Column(
        db.String(32),
        nullable=False,
        default="New Server"
    )

    create = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    owner = db.Column(
        db.Text,
        nullable=False
    )


class DmList(db.Model):
    __bind_key__ = "main"
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Text,
        primary_key=True,
        nullable=False,
        unique=True
    )


class RoomList(db.Model):
    __bind_key__ = "main"
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Text,
        primary_key=True,
        nullable=False,
        unique=True
    )


class Ban(db.Model):
    __bind_key__ = "main"
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Text,
        unique=True,
        primary_key=True,
        nullable=False
    )

    user = db.Column(
        db.Text,
        nullable=False
    )

    room = db.Column(
        db.Text,
        nullable=False
    )

    why = db.Column(
        db.String(2000),
        nullable=False,
        default="No reason."
    )


class Chat(db.Model):
    __bind_key__ = "chat"
    __tablename__ = "chat"

    id = db.Column(
        db.Text,
        unique=True,
        primary_key=True,
        nullable=False
    )

    room = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    content = db.Column(
        db.Text
    )
