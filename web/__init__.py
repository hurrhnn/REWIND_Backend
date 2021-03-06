from flask import Flask
from websocket.model import db
import secrets

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(32)

    db.init_app(app=app)

    from web import views
    for vp in views.__all__:
        app.register_blueprint(getattr(views, vp).bp)
    return app
