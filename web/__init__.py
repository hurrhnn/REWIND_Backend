from flask import Flask


def create_app():
    app = Flask(__name__)

    from web import views
    for vp in views.__all__:
        app.register_blueprint(getattr(views, vp).bp)
    return app
