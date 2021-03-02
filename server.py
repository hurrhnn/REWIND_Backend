from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

import api
import web
from websocket.protocol import WINDServerProtocol
from websocket.factory import WINDServerFactory

import sys

if __name__ == '__main__':
    log.startLogging(sys.stdout)

    ws_factory = WINDServerFactory("ws://127.0.0.1:8080")
    ws_factory.protocol = WINDServerProtocol
    ws_res = WebSocketResource(ws_factory)

    api_app = api.create_app()
    api_res = WSGIResource(reactor, reactor.getThreadPool(), api_app)

    web_app = web.create_app()
    web_res = WSGIResource(reactor, reactor.getThreadPool(), web_app)

    web_root_res = WSGIRootResource(web_res, {b'ws': ws_res, b'api': api_res})
    web_site = Site(web_root_res)

    reactor.listenTCP(8080, web_site)
    reactor.run()
