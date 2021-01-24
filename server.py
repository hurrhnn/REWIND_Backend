from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import json
import hmac
import base64


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
        }).encode("utf8")


class WINDServerProtocol(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sess_data = None

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            payload = get_data("error", {
                "code": 10000,
                "reason": "Binary data is not supported."
            })
            return self.sendMessage(payload, False)
        print("Text message received: {0}".format(payload.decode('utf8')))
        data = json.loads(payload.decode('utf-8'))
        print(data)
        if not self.sess_data:
            if data['type'] != "handshake":
                payload = get_data("error", {
                    "code": 10001,
                    "reason": "Please finish the handshake first."
                })
                return self.sendMessage(payload, False)
            data = data['payload']
            token = data.get("auth")
            if token is None:
                payload = get_data("error", {
                    "code": 10002,
                    "reason": "Token not provided."
                })
                return self.sendMessage(payload, False)
            jwt_body = jwt_decode(token)
            if not jwt_body:
                payload = get_data("error", {
                    "code": 10002,
                    "reason": "Token signature mismatch."
                })
                return self.sendMessage(payload, False)

            # TODO: retrieve data from SQL
            self.sess_data = {}
            self.sess_data['user'] = {
                "id": jwt_body['id'],
                "name": jwt_body['name'],
                "profile": None
            }
            friends = [{"id": 2, "name": "testuser2", "profile": None},
                       {"id": 3, "name": "tsetuser3", "profile": None}]

            payload = get_data("handshake", {
                "user_info": self.sess_data['user'],
                "friends": friends
            })
            return self.sendMessage(payload, False)

        self.sendMessage(payload, False)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


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
