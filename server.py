from websocket.protocol import WINDServerProtocol
from websocket.factory import WINDServerFactory

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WINDServerFactory("ws://0.0.0.0:9000")
    factory.protocol = WINDServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()
