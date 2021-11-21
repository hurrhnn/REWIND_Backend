import web
import warnings
import sys

from sqlalchemy import exc as sa_exc

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

from websocket.protocol import WINDServerProtocol
from websocket.factory import WINDServerFactory

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)

    ws_factory = WINDServerFactory("ws://0.0.0.0:9000")
    ws_factory.protocol = WINDServerProtocol
    ws_res = WebSocketResource(ws_factory)

    web_app = web.create_app()
    web_res = WSGIResource(reactor, reactor.getThreadPool(), web_app)

    web_root_res = WSGIRootResource(web_res, {b'ws': ws_res, b'web': web_res})
    web_site = Site(web_root_res)

    reactor.listenTCP(9000, web_site)
    reactor.run()
