from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))
        return None  # ask for defaults

    def onOpen(self):
        print("WebSocket connection open.")

        data = json.dumps({
            "type": "init",
            "meow": "asdf",
            "spam": "egg",
            "kyoko": "kirigiri"
        }).encode('utf8')

        self.sendMessage(data)

        def hello():
            self.sendMessage(b"\x00\x01\x03\x04", isBinary=True)
            self.sendMessage(json.dumps({"type": "req"}).encode('utf8'))
            self.factory.reactor.callLater(1, hello)

        # start sending messages every second ..
        hello()

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
            data = json.loads(payload.decode('utf8'))
            print(data['meow'])

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()
