from flask import Flask


def create_app():
    app = Flask(__name__)

    from .views import assets
    app.register_blueprint(assets)

    return app
