import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from Main import app,db

@pytest.fixture
def client():
    with app.app_context():
        cleanup()
        yield app.test_client()

def cleanup():
    db.drop_all()
    db.create_all()

def test_index_not_logged_in(client):
    response = client.get('/')
    assert b"Top 15 coins" in response.data

