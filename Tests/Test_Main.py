import pytest

from Main import db, create_app, Portfolio


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

def test_sign_up_password_mismatch(client):
    response = client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "test"},
                                            follow_redirects=True)
    #assert b"Passwords don&#39;t match!" in response.data
    assert b"Passwords don" in response.data
    assert b"t match!" in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(username='testuser').first()
    assert user is None

def test_sign_up_successful(client):
    response = client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "testpass"},
                                            follow_redirects=True)

    assert b"Account created successfully" in response.data
    assert b"Confirm password" not in response.data
    assert b"Password" in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'
    assert user.email == 'test@test'

def test_sign_up_duplicate_username(client):
    client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "testpass"},
                                            follow_redirects=True)
    response = client.post('/sign-up', data={"input_username": "testuser", "input_email": "test@test2",
                                             "input_password": "testpass2", "confirm_password": "testpass2"},
                           follow_redirects=True)
    assert b"Username already taken!" in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test2").first()
    assert user is None

def test_sign_up_missing_username(client):
    response = client.post('/sign-up', data={"input_email": "test@test","input_password": "testpass",
                                             "confirm_password": "testpass"},follow_redirects=True)
    assert b"All fields are required!" in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test").first()
    assert user is None

def test_sign_in_wrong_credentials(client):
    client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "testpass"},
                                            follow_redirects=True)
    response = client.post('/sign-in', data={"input_email": "test@test","input_password": "testpass2"},follow_redirects=True)
    assert b"Email or password is invalid!" in response.data
    assert b"Password" in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test").first()
    assert user.session_token is None

def test_sign_in_successful(client):
    client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "testpass"},
                                            follow_redirects=True)
    response = client.post('/sign-in', data={"input_email": "test@test","input_password": "testpass"},follow_redirects=True)
    assert b"login successful!" in response.data
    assert b'href="/sign-out"'  in response.data
    assert b'href="/add-coin"' in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test").first()
    assert user.session_token is not None

def test_sign_out_successful(client):
    client.post('/sign-up',data={"input_username": "testuser", "input_email": "test@test",
                                            "input_password": "testpass", "confirm_password": "testpass"},
                                            follow_redirects=True)
    client.post('/sign-in', data={"input_email": "test@test","input_password": "testpass"},follow_redirects=True)
    response = client.get('/sign-out', follow_redirects=True)
    assert b"Sign out successful!" in response.data
    assert b'href="/sign-in"'  in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test").first()
    assert user.session_token is None

def test_add_coin_not_in_db(client):
    client.post('/sign-up', data={"input_username": "testuser", "input_email": "test@test",
                                  "input_password": "testpass", "confirm_password": "testpass"},
                follow_redirects=True)
    client.post('/sign-in', data={"input_email": "test@test", "input_password": "testpass"}, follow_redirects=True)
    response = client.post("/add-coin", data={"coin_symbol": "ADR","quantity": 1,"total_paid": 1}, follow_redirects=True)
    assert b"not found in our database!" in response.data

def test_add_coin_successful(client):
    client.post('/sign-up', data={"input_username": "testuser", "input_email": "test@test",
                                  "input_password": "testpass", "confirm_password": "testpass"},
                follow_redirects=True)
    client.post('/sign-in', data={"input_email": "test@test", "input_password": "testpass"}, follow_redirects=True)

    from Main import Coin
    with client.application.app_context():
        test_coin = Coin(id = 1,rank =1, name= "ADA", symbol="ADA",price=1,mcap=10,volume ="5", change ="2")
        db.session.add(test_coin)
        db.session.commit()
    response = client.post("/add-coin", data={"coin_symbol": "ADA","quantity": 1,"total_paid": 1}, follow_redirects=True)
    assert b"Successfully added" in response.data

    from Main import Portfolio
    with client.application.app_context():
        portfolio_entry = Portfolio.query.filter_by(co_symbol="ADA").first()
        assert portfolio_entry is not None