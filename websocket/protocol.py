import json
import time

from autobahn.twisted.websocket import WebSocketServerProtocol
from sqlalchemy import create_engine, Table, MetaData, Column, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, mapper

from db.config import SQLALCHEMY_BINDS
from db.models import Chat, DmList, User
from util import jwt_decode, generate_snowflake
from websocket.util import error, heartbeat, handshake, chat

clients = {}


class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sess_data = None
        self.last_heartbeat = time.time()
        self.engine = {
            'main': create_engine(SQLALCHEMY_BINDS['main']),
            'chat': create_engine(SQLALCHEMY_BINDS['chat'])
        }

    def getDatabaseSession(self, name):
        return sessionmaker(bind=self.engine[name])()

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register(self)

    def onMessage(self, payload, is_binary):
        if is_binary:
            return self.sendMessage(
                error(10000, "Binary data not supported."),
                False
            )

        try:
            data = json.loads(payload)
        except ValueError:
            return self.sendMessage(
                error(10000, "Data should be JSON."),
                False
            )

        _type = data.get("type")
        data_payload = data.get("payload")
        if not (_type or data_payload):
            return self.sendMessage(
                error(10000, "Invalid request."),
                False
            )

        handler = self.func_map.get(f"{_type}")
        if handler is None:
            print(_type)
            return self.sendMessage(
                error(10000, "Unknown type."),
                False
            )
        print(payload.decode())
        return self.sendMessage(handler(self, data_payload))

    def onClose(self, _, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def onConnectionLost(self, reason):
        super(WebSocketServerProtocol, self).connectionLost(reason)
        self.factory.unregister(self)

    def onHeartbeat(self, payload):
        # TODO: Check heartbeat
        self.last_heartbeat = time.time()
        return heartbeat(payload)

    def onHandshake(self, payload):
        token = payload.get("auth")
        if not token:
            return error(10002, "Token not provided.")

        jwt_body = jwt_decode(token)
        if not jwt_body:
            return error(10002, "Token signature mismatch.")

        print(jwt_body)
        self.sess_data = dict()
        self.sess_data['user'] = {
            "id": jwt_body['id'],
            "name": jwt_body['name'],
            "profile": None
        }

        friends = []
        session = self.getDatabaseSession('main')
        for user in session.query(User).all():
            if self.sess_data['user']['id'] == user.id:
                continue

            user_dict = {
                "id": user.id,
                "name": user.name
            }

            user_dict.update({"profile": None})
            friends.append(user_dict)
        #   가입되어있는 유저 친구

        clients.update({jwt_body['id']: self})
        return handshake(self.sess_data, friends)

    def onChat(self, payload):
        _type = payload['type']
        user_id = self.sess_data['user']['id']

        if _type not in ["send", "edit"]:
            return error(10003, "Unknown chat type.")

        session = self.getDatabaseSession('main')
        dm_exist = session.query(DmList).filter_by(id=payload['chat_id']).first()

        metadata = MetaData(self.engine['chat'])
        table = Table('DM_' + payload['chat_id'],
                      metadata,
                      Column('id', Text, unique=True, primary_key=True, nullable=False),
                      Column('room', Text, nullable=False),
                      Column('author', Text, nullable=False),
                      Column('timestamp', DateTime, default=func.now()),
                      Column('content', Text),
                      )

        mapper(Chat, table, non_primary=True)

        if dm_exist is None:
            session.add(DmList(id=payload['chat_id']))
            session.commit()
            metadata.create_all(self.engine['chat'])

        if _type == "send":
            if not payload['content']:
                return error(10004, "content is not provided.")

            client = clients.get(str(int(payload['chat_id']) ^ int(user_id)))

            session = self.getDatabaseSession('chat')
            _id = generate_snowflake(self.getDatabaseSession('main'))
            session.add(Chat(__tablename__='DM_' + payload['chat_id'],
                             id=_id,
                             room=payload['chat_id'],
                             author=user_id,
                             content=payload['content']))
            session.commit()

            try:
                client.sendMessage(chat(_type, _id, user_id, payload['chat_id'], payload['content']))
            except AttributeError:
                pass

        else:
            session = self.getDatabaseSession('chat')
            _id = generate_snowflake(self.getDatabaseSession('main'))

            if not payload['content']:
                session.query(Chat).filter_by(id=payload['id']).delete(
                    synchronize_session='fetch')
                session.commit()

            else:
                session.query(Chat).filter_by(id=payload['id']).update(
                    {'content': payload['content'],
                     'id': _id,
                     'timestamp': func.now()})
                session.commit()
        return chat(_type, _id, user_id, payload['chat_id'], payload['content'])

    def onLoad(self, payload):
        print(self)

    func_map = {
        "heartbeat": onHeartbeat,
        "handshake": onHandshake,
        "chat": onChat,
        "load": onLoad
    }
