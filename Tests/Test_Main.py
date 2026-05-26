import pytest

from Main import db, create_app, Coin, Portfolio


@pytest.fixture
def client():

                        #passing dictionary as an argument
    app = create_app({"SQLALCHEMY_DATABASE_URI" : "sqlite:///:memory:", "TESTING" : True})

    with app.app_context():
        print(f"TEST ENGINE: {db.engine.url}")
        db.drop_all()
        db.create_all()
        yield app.test_client()

@pytest.fixture
def client_logged(client):
    client.post('/sign-up', data={"input_username": "testuser", "input_email": "test@test",
                                  "input_password": "testpass", "confirm_password": "testpass"},
                follow_redirects=True)
    client.post('/sign-in', data={"input_email": "test@test", "input_password": "testpass"}, follow_redirects=True)
    return client

def add_coin_to_db(client, id = 1,rank =1, name= "ADA", symbol="ADA",price=1,mcap=10,volume ="5", change ="2"):
    with client.application.app_context():
        testcoin = Coin(
            id = id,
            rank = rank,
            name = name,
            symbol = symbol,
            price = price,
            mcap = mcap,
            volume = volume,
            change = change
        )
        db.session.add(testcoin)
        db.session.commit()

def add_coin_to_portfolio(client):
    return client.post("/add-coin",
                       data={"coin_symbol": "ADA","quantity": 1,"total_paid": 1},
                       follow_redirects=True)




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

def test_sign_out_successful(client_logged):
    response = client_logged.get('/sign-out', follow_redirects=True)
    assert b"Sign out successful!" in response.data
    assert b'href="/sign-in"'  in response.data

    from Main import Ptracker
    user = Ptracker.query.filter_by(email="test@test").first()
    assert user.session_token is None

def test_add_coin_not_in_db(client_logged):
    response = client_logged.post("/add-coin", data={"coin_symbol": "ADR","quantity": 1,"total_paid": 1}, follow_redirects=True)
    assert b"not found in our database!" in response.data

def test_add_coin_successful(client_logged):
    add_coin_to_db(client_logged)
    response = add_coin_to_portfolio(client_logged)
    assert b"Successfully added" in response.data

    from Main import Portfolio
    with client_logged.application.app_context():
        portfolio_entry = Portfolio.query.filter_by(co_symbol="ADA").first()
        assert portfolio_entry is not None

def test_coin_overview(client_logged):
    add_coin_to_db(client_logged)
    add_coin_to_portfolio(client_logged)
    response = client_logged.get("overview/ADA", follow_redirects=True)
    assert b"ADA - overview" in response.data

def test_delete_1_out_of_1_transaction(client_logged):
    add_coin_to_db(client_logged)
    add_coin_to_portfolio(client_logged)
    client_logged.get("overview/ADA", follow_redirects=True)
    response = client_logged.get("/delete-transaction/1/1", follow_redirects=True)
    assert b"transaction deleted" in response.data
    assert b'href="/add-coin"' in response.data

def test_delete_1_out_of_more_transaction(client_logged):
    add_coin_to_db(client_logged)
    for _ in range(2):
        add_coin_to_portfolio(client_logged)
    client_logged.get("overview/ADA", follow_redirects=True)
    response = client_logged.get("/delete-transaction/1/2", follow_redirects=True)
    assert b"transaction deleted" in response.data
    assert b"ADA - overview" in response.data

def test_edit_transaction(client_logged):
    add_coin_to_db(client_logged)
    add_coin_to_portfolio(client_logged)
    client_logged.get("overview/ADA", follow_redirects=True)

    response1 = client_logged.get("/edit-transaction/1", follow_redirects=True)
    assert b"Edit transaction" in response1.data
    from Main import Portfolio
    with client_logged.application.app_context():
        portfolio_old = Portfolio.query.filter_by(co_symbol="ADA").first()
        assert portfolio_old.quantity == 1
        assert portfolio_old.total_paid == 1

    response2 = client_logged.post("/edit-transaction/1", data = {"quantity": 2,"total_paid": 2}, follow_redirects=True)
    assert b"ADA - overview" in response2.data
    with client_logged.application.app_context():
        portfolio_new = Portfolio.query.filter_by(co_symbol="ADA").first()
        assert portfolio_new.quantity == 2
        assert portfolio_new.total_paid == 2