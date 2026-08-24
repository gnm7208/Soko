import os

from flask import Flask, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from server.config import config_by_name
from server.extensions import db, init_extensions


def create_app():
    app = Flask(__name__)
    env = os.getenv("ENV", "development")
    app.config.from_object(config_by_name[env])

    if env == "production":
        # Render (and most PaaS) terminate TLS at the edge and forward plain HTTP
        # internally with X-Forwarded-Proto: https. Without ProxyFix, Talisman's
        # force_https never sees a secure request and redirect-loops forever.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    init_extensions(app)

    with app.app_context():
        pass

    from server.routes.admin import bp as admin_bp
    from server.routes.auth import bp as auth_bp
    from server.routes.categories import bp as categories_bp
    from server.routes.chat import bp as chat_bp
    from server.routes.deliveries import bp as deliveries_bp
    from server.routes.disputes import bp as disputes_bp
    from server.routes.favorites import bp as favorites_bp
    from server.routes.listings import bp as listings_bp
    from server.routes.notifications import bp as notifications_bp
    from server.routes.orders import bp as orders_bp
    from server.routes.payments import bp as payments_bp
    from server.routes.profiles import bp as profiles_bp
    from server.routes.promotions import bp as promotions_bp
    from server.routes.reviews import bp as reviews_bp
    from server.routes.search import bp as search_bp
    from server.routes.shops import bp as shops_bp
    from server.routes.wallets import bp as wallets_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1")
    app.register_blueprint(profiles_bp, url_prefix="/api/v1")
    app.register_blueprint(shops_bp, url_prefix="/api/v1")
    app.register_blueprint(categories_bp, url_prefix="/api/v1")
    app.register_blueprint(listings_bp, url_prefix="/api/v1")
    app.register_blueprint(favorites_bp, url_prefix="/api/v1")
    app.register_blueprint(search_bp, url_prefix="/api/v1")
    app.register_blueprint(chat_bp, url_prefix="/api/v1")
    app.register_blueprint(orders_bp, url_prefix="/api/v1")
    app.register_blueprint(payments_bp, url_prefix="/api/v1")
    app.register_blueprint(deliveries_bp, url_prefix="/api/v1")
    app.register_blueprint(disputes_bp, url_prefix="/api/v1")
    app.register_blueprint(reviews_bp, url_prefix="/api/v1")
    app.register_blueprint(promotions_bp, url_prefix="/api/v1")
    app.register_blueprint(wallets_bp, url_prefix="/api/v1")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1")

    @app.get("/static/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["STORAGE_PATH"], filename)

    @app.get("/api/health")
    def health():
        try:
            db.session.execute("SELECT 1")
            db_status = "ok"
        except Exception:
            db_status = "error"

        return jsonify({"status": "ok", "database": db_status, "env": env})

    if app.config.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()], environment=env
        )

    from server.services.socketio_chat import ChatNamespace
    from server.extensions import socketio

    socketio.on_namespace(ChatNamespace("/chat"))

    return app
