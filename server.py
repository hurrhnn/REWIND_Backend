from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import json
import hmac
import base64
import time


clients = {}


def b64_fix(data):
    return data + b"="*((4 - len(data) % 4) if len(data) % 4 != 0 else 0)


def jwt_decode(jwt, secret=b"testsecretkey"):
    body_verify = jwt.rsplit(".", 1)[0]
    header, body, sig = [
        base64.urlsafe_b64decode(b64_fix(data.encode()))
        for data in jwt.split(".")]
    header, body = map(json.loads, (header, body))
    if hmac.digest(secret, body_verify.encode(), digest="sha256") != sig:
        return False
    return body


def get_data(type, payload):
    return json.dumps({
        "type": type,
        "payload": payload
    }).encode("utf-8")


def error(code, reason):
    return get_data("error", {
        "code": code,
        "reason": reason
    })


def chat(type, user_id, chat_id, content):
    return get_data("chat", {
        "type": type,
        "user_id": user_id,
        "chat_id": chat_id,
        "content": content
    })


class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sess_data = None
        self.last_heartbeat = time.time()

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

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

        handler = self.func_map.get(_type)
        if handler is None:
            return self.sendMessage(
                error(10000, "Unknown type."),
                False
            )

        return handler(self, data_payload)

    def on_heartbeat(self, payload):
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
        self.sess_data = dict()
        self.sess_data['user'] = {
            "id": jwt_body['id'],
            "name": jwt_body['name'],
            "profile": None
        }
        friends = [{"id": 2, "name": "testuser2", "profile": None},
                   {"id": 3, "name": "tsetuser3", "profile": None}]
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

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    func_map = {
        "heartbeat": on_heartbeat,
        "handshake": on_handshake,
        "chat": on_chat
    }


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = WINDServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()
