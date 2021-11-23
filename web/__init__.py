import os

from flask import Blueprint
from flask import Flask
from flask_mailing import Mail
from flask_sqlalchemy import SQLAlchemy

from db.config import SQLALCHEMY_BINDS
from util import secret

db = SQLAlchemy()
mail = Mail()
mail_verify = {}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret()
    app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_USERNAME'] = os.environ['MAIL_ADDRESS']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWD']
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_SERVER'] = "smtp.icmp.kr"
    app.config['MAIL_TLS'] = False
    app.config['MAIL_SSL'] = False

    db.init_app(app=app)
    mail.init_app(app)

    with app.app_context():
        db.create_all(["main"])

        from db.models import ModelCreator
        counter = ModelCreator.get_model("counter").query.first()
        if counter is None:
            counter = ModelCreator.get_model("counter")()
            counter.count = 0

            db.session.add(counter)
            db.session.commit()

    from web import views
    for vp in views.__all__:
        app.register_blueprint(getattr(views, vp).bp)

    api_root = Blueprint(
        name="api",
        import_name="api",
        url_prefix="/api"
    )

    from . import api
    for api_version in api.__all__:
        api_root.register_blueprint(getattr(getattr(api, api_version), "bp"))

    app.register_blueprint(api_root)

    return app
