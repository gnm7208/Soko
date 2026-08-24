import os

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
socketio = SocketIO(cors_allowed_origins=os.getenv("CORS_ORIGINS", "").split(","))
api = Api()
cors = CORS()

csp = {
    "default-src": ["'self'"],
    "img-src": ["'self'", "data:", "https:"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
}


def init_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    allowed_origins = [origin.strip() for origin in app.config.get("CORS_ORIGINS", "").split(",") if origin.strip()]
    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    if app.config["ENV"] == "production":
        Talisman(app, content_security_policy=csp, force_https=True)
    else:
        Talisman(app, content_security_policy=csp, force_https=False)

    api.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("CORS_ORIGINS", "").split(","),
        logger=app.config["ENV"] == "development",
        engineio_logger=app.config["ENV"] == "development",
    )
