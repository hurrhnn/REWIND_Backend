import base64
import json
import time
from datetime import datetime, timedelta

from pytz import timezone

from autobahn.twisted.websocket import WebSocketServerProtocol
from sqlalchemy import create_engine, desc, MetaData
from sqlalchemy.orm import sessionmaker

from db.config import SQLALCHEMY_BINDS
from db.models import ModelCreator
from util import jwt_decode, generate_snowflake
from websocket.util import error, heartbeat, authenticate, chat, load, mutual_users


# WebSocket Close Codes: https://github.com/Luka967/websocket-close-codes
class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticated = False
        self.sess_data = None
        self.last_heartbeat = time.time()
        self.engines = {name: create_engine(uri) for name, uri in SQLALCHEMY_BINDS.items()}
        self.sessions = {name: sessionmaker(engine) for name, engine in self.engines.items()}
        self.metadata = {name: MetaData(engine) for name, engine in self.engines.items()}

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

        data = handler(self, data_payload)
        if data is not None:
            print(json.dumps(json.loads(data), indent=4))
            return self.sendMessage(data)

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

        session = self.sessions['main']()

        self.authenticated = True
        return authenticate(self.sess_data, session.query(ModelCreator.get_model('user')).filter_by(
            id=self.sess_data['user']['id']).first().mutual_users)

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
            return error(4004, "User not exist.")

        chat_model = ModelCreator.get_model("chat", "DM_" + payload['chat_id'])

        if dm_exist is None:
            session.add(ModelCreator.get_model("dm_list")(id=payload['chat_id']))
            session.commit()
            chat_model.__table__.create(bind=self.engines['chat'])

        created_at = datetime.now(timezone('Asia/Seoul'))

        query_result = True
        if _type == "send":
            if not payload['content']:
                return error(4000, "content is not provided.")

            clients = list(filter(lambda x: x.sess_data['user']['id'] == str(int(payload['chat_id']) ^ int(user_id)),
                                  self.factory.clients))

            _id = generate_snowflake(self.sessions['main']())
            session = self.sessions['chat']()

            session.add(chat_model(id=_id,
                                   room=payload['chat_id'],
                                   author=user_id,
                                   created_at=created_at,
                                   content=payload['content']))
            session.commit()

            for client in clients:
                client.sendMessage(chat(_type, _id, user_id, payload['chat_id'], str(created_at), payload['content']))

        else:
            _id = generate_snowflake(self.sessions['main']())
            session = self.sessions['chat']()

            if not payload['content']:
                query_result = bool(session.query(chat_model).filter_by(id=payload['id'],
                                                                        author=self.sess_data['user']).delete(
                    synchronize_session='fetch'))
                session.commit()

            else:
                query_result = bool(session.query(chat_model).filter_by(id=payload['id'],
                                                                        author=self.sess_data['user']['id']).update(
                    {'content': payload['content'],
                     'id': _id}))
                session.commit()
        return chat(_type, _id, user_id, payload['chat_id'], str(created_at),
                    payload['content']) if query_result else None

    def onLoad(self, payload):
        if self.authenticated is False:
            return error(4001, "Authentication required.")

        _type = payload['type']

        if _type not in ["chat"]:
            return error(4000, "Unknown load type.")

        main_session = self.sessions['main']()
        if _type == "chat":
            chat_session = self.sessions['chat']()
            load_id = payload['load_id']
            created_at = payload['datetime']
            count = payload['count']
            if main_session.query(ModelCreator.get_model("user")).filter_by(
                    id=str(int(load_id) ^ int(self.sess_data['user']['id']))).first():
                if main_session.query(ModelCreator.get_model("dm_list")).filter_by(id=load_id).first():
                    chat_model = ModelCreator.get_model("chat", "DM_" + load_id)
                    queried_data = chat_session.query(chat_model).filter(
                        chat_model.created_at < datetime.strptime(base64.b64decode(created_at).decode('utf-8'),
                                                                  "%Y-%m-%d %H:%M:%S.%f") - timedelta(
                            hours=-9)).order_by(desc(chat_model.created_at)).limit(
                        count).all()
                    if queried_data:
                        [self.sendMessage(load(x)) for x in list(
                            map(lambda x: json.loads(
                                chat("type", x.id, x.author, x.room, str(x.created_at), x.content)),
                                queried_data))[::-1]]
                    return None
            else:
                return error(4004, "provided DM is not opened.")

    def onMutualUsers(self, payload):
        if self.authenticated is False:
            return error(4001, "Authentication required.")

        _type = payload['type']
        if _type not in ["request", "response", "retrieve", "remove"]:
            return error(4004, "Unknown mutual_users type.")

        main_session = self.sessions['main']()
        if _type == 'retrieve':
            if payload.get('name') is None:
                _mutual_users = [{
                    "id": user.id,
                    "name": user.name,
                    "profile": None
                } for user in
                    main_session.query(ModelCreator.get_model("user")).all() if
                    self.sess_data['user']['id'] != user.id]
                return load(_mutual_users)
            else:
                return None

        elif _type == 'request':
            check = main_session.query(ModelCreator.get_model('user')).filter_by(
                id=self.sess_data['user']['id']).first()

            if [payload['name'] for i in json.loads(check.mutual_users) if i['name'] == payload['name']]:
                return error(4000, "mutual_user is already exist.")
            else:
                req_pending_queue = json.loads(main_session.query(ModelCreator.get_model('user')).filter_by(
                    name=payload['name']).first().req_pending_queue)

                check = main_session.query(ModelCreator.get_model('user')).filter_by(name=payload['name']).update(
                        {
                            'req_pending_queue': json.dumps(req_pending_queue if
                                                            req_pending_queue and self.sess_data['user']['id']
                                                            in req_pending_queue else [self.sess_data['user']['id']]
                                                            if not req_pending_queue else
                                                            req_pending_queue.append(self.sess_data['user']['id']))
                        })
                main_session.commit()

                if check:
                    return mutual_users(_type, payload['name'])

                else:
                    return error(4004, "could not send to request mutual_user.")

        elif _type == 'response':
            return None

        elif _type == 'delete':
            return None

        elif _type == 'remove':
            return None

    func_map = {
        "heartbeat": onHeartbeat,
        "auth": onAuthenticate,
        "chat": onChat,
        "load": onLoad,
        "mutual_users": onMutualUsers
    }
