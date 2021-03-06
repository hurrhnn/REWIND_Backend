from autobahn.twisted.websocket import WebSocketServerFactory


class WINDServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(WebSocketServerFactory, self).__init__(*args, **kwargs)
        self.clients = []

    def register(self, client):
        self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)
