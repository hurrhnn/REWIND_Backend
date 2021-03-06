import json
import time

from autobahn.twisted.websocket import WebSocketServerProtocol

from util import jwt_decode
from websocket.util import get_data, error, chat

from websocket.model import User

clients = {}


class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sess_data = None
        self.last_heartbeat = time.time()

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
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

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def connectionLost(self, reason):
        super(WebSocketServerProtocol, self).connectionLost(reason)
        self.factory.unregister(self)

    def on_heartbeat(self, payload):
        # TODO: Check heartbeat
        self.last_heartbeat = time.time()
        return get_data("heartbeat", payload)

    def on_handshake(self, payload):
        # TODO: retrieve data from SQL
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
        # friends = [{"id": 1, "name": "hurrhnn", "profile": None},
        #            {"id": 2, "name": "chick_0", "profile": None},
        #            {"id": 3, "name": "tsetuser3", "profile": None}]

        friends = []

        for user in User.query.all():
            Udict = json.loads(str(user))
            Udict.update({"profile": None})
            friends.append(Udict)
            # print(friends)

        friends.remove({"id": jwt_body['id'], "name": jwt_body['name'], "profile": None})
        clients.update({jwt_body['id']: self})
        return get_data("handshake", {
            "user_info": self.sess_data['user'],
            "friends": friends
        })

    def on_chat(self, payload):
        _type = payload['type']
        user_id = self.sess_data['user']['id']

        if _type not in ["send", "edit"]:
            return error(10003, "Unknown chat type.")
        client = clients.get(payload['chat_id'])
        if payload is None:
            return error(10004, "Chatroom not found.")
        client.sendMessage(chat(_type, user_id, user_id, payload['content']))
        return chat(_type, user_id, payload['chat_id'], payload['content'])

    func_map = {
        "heartbeat": on_heartbeat,
        "handshake": on_handshake,
        "chat": on_chat
    }
