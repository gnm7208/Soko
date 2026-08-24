import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["ENV"] = "testing"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"


@pytest.fixture
def app():
    from server.app import create_app

    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from server.extensions import db

        db.create_all()
    return app


@pytest.fixture
def client(app):
    return app.test_client()
