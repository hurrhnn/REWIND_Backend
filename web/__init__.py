from flask import Flask
from websocket.model import db

from util import secret

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret()

    db.init_app(app=app)

    from web import views
    for vp in views.__all__:
        app.register_blueprint(getattr(views, vp).bp)
    return app
