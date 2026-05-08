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
    assert b'href="/sign-up"' in response.data
    assert b'href="/sign-in"' in response.data
    assert b'href="/sign-out"' not in response.data

def test_sign_up_link_from_index_not_logged_in(client):
    response = client.get('/')
    assert b'href="/sign-up"' in response.data

    response = client.get('/sign-up')
    assert b"Confirm password" in response.data

def test_sign_in_link_from_index_not_logged_in(client):
    response = client.get('/')
    assert b'href="/sign-in"' in response.data

    response = client.get('/sign-in')
    assert b"Password" in response.data
    assert b"Confirm password" not in response.data

def test_sign_up_hide_header_links(client):
    response = client.get('/sign-up')
    assert b'href="/sign-up"' not in response.data
    assert b'href="/sign-in"' not in response.data

def test_sign_in_hide_header_links(client):
    response = client.get('/sign-in')
    assert b'href="/sign-up"' not in response.data
    assert b'href="/sign-in"' not in response.data