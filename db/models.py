import re
from pytz import timezone
from datetime import datetime

from web import db


class ModelCreator:
    @classmethod
    def get_model(cls, type_, table_name=None):
        custom_table_name_map = {
            "counter": "snowflake_counter"
        }

        if table_name is None:
            table_name = custom_table_name_map.get(type_.lower(), type_.lower())

        handler = getattr(cls, f"get_{type_.lower()}_model", None)

        if handler is None:
            raise TypeError("Unknown model type.")

        metadata = db.metadata
        prev_table = metadata.tables.get(table_name)
        if prev_table is not None:
            metadata.remove(prev_table)

        return handler(table_name)

    @classmethod
    def get_counter_model(cls, table_name=None):
        class Counter(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "snowflake_counter"

            count = db.Column(
                db.Integer,
                primary_key=True,
                nullable=False
            )

        return Counter

    @classmethod
    def get_user_model(cls, table_name=None):
        class User(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "user"

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

            created_at = db.Column(
                db.DateTime,
                default=datetime.now(timezone('Asia/Seoul')),
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

            server = db.Column(
                db.Text,
                default="[]",
                nullable=True
            )

            mutual_users = db.Column(
                db.Text,
                default="[]",
                nullable=True
            )

            req_pending_queue = db.Column(
                db.Text,
                default="[]",
                nullable=True
            )

            profile = db.Column(
                db.Text,
                nullable=True,
                default=None
            )

        return User

    @classmethod
    def get_room_model(cls, table_name=None):
        class Room(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "room"

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

            created_at = db.Column(
                db.DateTime,
                nullable=False,
                default=datetime.now(timezone('Asia/Seoul'))
            )

            owner = db.Column(
                db.Text,
                nullable=False
            )

        return Room

    @classmethod
    def get_dm_list_model(cls, table_name=None):
        class DmList(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "dm_list"
            id = db.Column(
                db.Text,
                primary_key=True,
                nullable=False,
                unique=True
            )

        return DmList

    @classmethod
    def get_room_list_model(cls, table_name=None):
        class RoomList(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "room_list"
            id = db.Column(
                db.Text,
                primary_key=True,
                nullable=False,
                unique=True
            )

        return RoomList

    @classmethod
    def get_ban_model(cls, table_name=None):
        class Ban(db.Model):
            __bind_key__ = "main"
            __tablename__ = table_name if table_name else "ban"

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

        return Ban

    @classmethod
    def get_chat_model(cls, table_name=None):
        class Chat(db.Model):
            __bind_key__ = "chat"
            __tablename__ = table_name if table_name else "chat"

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

            created_at = db.Column(
                db.DateTime,
                nullable=False,
                default=datetime.now(timezone('Asia/Seoul'))
            )

            content = db.Column(
                db.Text
            )

        return Chat


model_regex = re.compile("get_(.*?)_model")
for func_name in [model_regex.search(x).groups()[0] for x in dir(ModelCreator) if model_regex.match(x)]:
    ModelCreator.get_model(func_name)
