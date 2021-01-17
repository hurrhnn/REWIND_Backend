from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import json


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
            # echo back message verbatim
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
            data = json.loads(payload.decode('utf-8'))
            print(data)
            if data['type'] == "init":
                self.meow_data = payload
            elif data['type'] == "req":
                payload = self.meow_data

        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory("ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()
