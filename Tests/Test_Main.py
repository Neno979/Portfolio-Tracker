import pytest

from Main import db, create_app


@pytest.fixture
def client():
                        #passing dictionary as an argument
    app = create_app({"SQLALCHEMY_DATABASE_URI" : "sqlite:///:memory:", "TESTING" : True})

    with app.app_context():
        print(f"TEST ENGINE: {db.engine.url}")
        db.drop_all()
        db.create_all()
        yield app.test_client()


def test_index_not_logged_in(client):
    response = client.get('/')
    assert b"Top 15 coins" in response.data

