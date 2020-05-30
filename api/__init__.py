from flask import Flask 

"""
Environment Variables:
    export FLASK_APP=api
    export FLASK_DEBUG=1
"""

def create_app():
    app = Flask(__name__)

    from .views import assets
    app.register_blueprint(assets)

    return app