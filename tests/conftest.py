import pytest

from app import create_app
from app.extensions import db
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, name="asha", email="asha@example.com", pw="secret123"):
    return client.post("/auth/register", data={"username": name, "email": email, "password": pw, "confirm": pw},
                       follow_redirects=True)
