from datetime import datetime

from sqlalchemy import func

from web import db


class Counter(db.Model):
    __tablename__ = "snowflake_counter"

    count = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False
    )


class User(db.Model):
    __tablename__ = "users"

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
    __tablename__ = "room"

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
    __tablename__ = "dm_list"
    id = db.Column(
        db.Text,
        primary_key=True,
        nullable=False,
        unique=True
    )


class RoomList(db.Model):
    __tablename__ = "room_list"
    id = db.Column(
        db.Text,
        primary_key=True,
        nullable=False,
        unique=True
    )


class Ban(db.Model):
    __tablename__ = "ban"

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


class ModelCreator:
    @classmethod
    def get_model(cls, type_, table_name):
        handler = getattr(cls, f"get_{type_.lower()}_model", None)

        if handler is None:
            raise TypeError("Unknown model type!")

        return handler(table_name)

    @classmethod
    def get_chat_model(cls, table_name):
        class KingGodGeneralEmperorChungmugongChat(db.Model):
            __tablename__ = table_name
    
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
    
        return KingGodGeneralEmperorChungmugongChat
