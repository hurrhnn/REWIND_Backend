from flask import Flask
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

from db.config import SQLALCHEMY_BINDS
from util import secret

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret()
    app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app=app)

    with app.app_context():
        db.create_all(["main", "chat"])

        from db.models import Counter
        counter = Counter.query.first()
        if counter is None:
            counter = Counter()
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
