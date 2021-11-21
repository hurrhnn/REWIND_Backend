import json
import time

from autobahn.twisted.websocket import WebSocketServerProtocol
from sqlalchemy import create_engine, MetaData, func
from sqlalchemy.orm import sessionmaker

from db.config import SQLALCHEMY_BINDS
from db.models import ModelCreator
from util import jwt_decode, generate_snowflake
from websocket.util import error, heartbeat, authenticate, chat


# WebSocket Close Codes: https://github.com/Luka967/websocket-close-codes
class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticated = False
        self.sess_data = None
        self.last_heartbeat = time.time()
        self.engines = {name: create_engine(uri) for name, uri in SQLALCHEMY_BINDS.items()}
        self.sessions = {name: sessionmaker(engine) for name, engine in self.engines.items()}
        self.metadatas = {name: MetaData(engine) for name, engine in self.engines.items()}

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register(self)

    def onMessage(self, payload, is_binary):
        if is_binary:
            return self.sendMessage(
                error(1003, "Binary data not supported."),
                False
            )

        try:
            data = json.loads(payload)
            _type = data.get("type")
            data_payload = data.get("payload")

        except (ValueError, AttributeError):
            return self.sendMessage(
                error(1007, "Data should be JSON."),
                False
            )

        if not (_type or data_payload):
            return self.sendMessage(
                error(4000, "Invalid request."),
                False
            )

        handler = self.func_map.get(f"{_type}")
        if handler is None:
            return self.sendMessage(
                error(4000, "Unknown type."),
                False
            )

        print(json.dumps(data, indent=4))
        return self.sendMessage(handler(self, data_payload))

    def onClose(self, _, code, reason):
        self.factory.unregister(self)
        print("WebSocket connection closed: {0}".format(reason))

    def onConnectionLost(self, reason):
        super(WebSocketServerProtocol, self).connectionLost(reason)
        self.factory.unregister(self)

    def onHeartbeat(self, payload):
        # TODO: Check heartbeat
        self.last_heartbeat = time.time()
        return heartbeat(payload)

    def onAuthenticate(self, payload):
        token = payload.get("auth")
        if not token:
            return error(4000, "Token not provided.")

        jwt_body = jwt_decode(token)
        if not jwt_body:
            return error(4000, "Token signature mismatch.")

        print(jwt_body)
        self.sess_data = dict()
        self.sess_data['user'] = {
            "id": jwt_body['id'],
            "name": jwt_body['name'],
            "profile": None
        }

        friends = []
        session = self.sessions['main']()
        for user in session.query(ModelCreator.get_model("user")).all():
            if self.sess_data['user']['id'] == user.id:
                continue

            user_dict = {
                "id": user.id,
                "name": user.name
            }

            user_dict.update({"profile": None})
            friends.append(user_dict)

        self.authenticated = True
        return authenticate(self.sess_data, friends)

    def onChat(self, payload):
        if self.authenticated is False:
            return error(4001, "Authentication required.")

        _type = payload['type']
        user_id = self.sess_data['user']['id']

        if _type not in ["send", "edit"]:
            return error(4000, "Unknown chat type.")

        session = self.sessions['main']()
        dm_check = session.query(ModelCreator.get_model("user")).filter_by(
            id=str(int(payload['chat_id']) ^ int(user_id))).first()
        dm_exist = session.query(ModelCreator.get_model("dm_list")).filter_by(id=payload['chat_id']).first()

        if dm_check is None:
            return error(4000, "Unknown chat type.")

        Chat = ModelCreator.get_model("chat", "DM_" + payload['chat_id'])

        if dm_exist is None:
            session.add(ModelCreator.get_model("dm_list")(id=payload['chat_id']))
            session.commit()
            Chat.__table__.create(bind=self.engines['chat'])

        if _type == "send":
            if not payload['content']:
                return error(4000, "content is not provided.")

            clients = list(filter(lambda x: x.sess_data['user']['id'] == str(int(payload['chat_id']) ^ int(user_id)),
                                  self.factory.clients))

            _id = generate_snowflake(self.sessions['main']())
            session = self.sessions['chat']()

            session.add(Chat(id=_id,
                             room=payload['chat_id'],
                             author=user_id,
                             content=payload['content']))
            session.commit()

            for client in clients:
                client.sendMessage(chat(_type, _id, user_id, payload['chat_id'], payload['content']))

        else:
            _id = generate_snowflake(self.sessions['main']())
            session = self.sessions['chat']()

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
        # TODO: Retrieve chat from database.
        if self.authenticated is False:
            return error(4001, "Authentication required.")

        return self

    func_map = {
        "heartbeat": onHeartbeat,
        "auth": onAuthenticate,
        "chat": onChat,
        "load": onLoad
    }
