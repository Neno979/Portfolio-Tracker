from enum import unique

from flask import Flask, render_template, request, redirect, flash, make_response
from flask_sqlalchemy import SQLAlchemy
import requests
import uuid




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
app.config['SECRET_KEY'] = 'Gigaj_Kokana'
db = SQLAlchemy(app)

class Ptracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    session_token = db.Column(db.String, unique=True, nullable=True)

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    symbol = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    mcap = db.Column(db.Float, unique=False, nullable=False)
    volume = db.Column(db.Float, unique=False, nullable=False)
    change = db.Column(db.Float, unique=False, nullable=False)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ptracker.id'), nullable=False)
    co_symbol = db.Column(db.String, unique=False, nullable=False)
    co_name = db.Column(db.String, unique=False, nullable=False)
    quantity = db.Column(db.Float, unique=False, nullable=False)
    total_paid = db.Column(db.Float, unique=False, nullable=False)
    user = db.relationship('Ptracker', backref=db.backref('portfolio', lazy=True))

    def format_value(self, value):
        if value >= 100_000_000_000:
            return f"{value / 1_000_000_000_000:.2f}T"
        elif value >= 100_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 100_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 100:
            return f"{value / 1_000:.2f}k"
        else:
            return f"{value:.2f}"

    @property
    def formatted_price(self):
        return self.format_value(self.price)

    @property
    def formatted_mcap(self):
        return self.format_value(self.mcap)

    @property
    def formatted_volume(self):
        return self.format_value(self.volume)

with app.app_context():
    db.create_all()

@app.route("/")
def index():


    theads = ["#", "Price", "M.Cap.", "24hVol.", "24h%"]
    API_KEY = "coinranking6ae704e6e7974096325d95be12cd9c383994de673acb79bf"
    url = "https://api.coinranking.com/v2/coins?limit=15"
    headers = {"x-access-token": API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    coins_data = data['data']['coins']
    coins = Coin.query.order_by(Coin.rank).all()

    Coin.query.delete()
    for coin_data in coins_data:
        new_coin = Coin(
            rank=int(coin_data['rank']),
            name=coin_data['name'],
            symbol=coin_data['symbol'],
            price=float(coin_data['price']),
            mcap=float(coin_data['marketCap']),
            volume=float(coin_data['24hVolume']),
            change=float(coin_data['change'])
        )
        db.session.add(new_coin)

    db.session.commit()

    session_token = request.cookies.get("session_token")

    if session_token:
        user = Ptracker.query.filter_by(session_token=session_token).first()
        if user:
            return redirect("/portfolio")

    return render_template("index.html", theads = theads, coins = coins)

@app.route("/portfolio" , methods=["GET", "POST"])
def portfolio():
    # Get session_token from cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        flash("Please login first!", "warning")
        return redirect("/sign-in")
    user = Ptracker.query.filter_by(session_token=session_token).first()
    if not user:
        flash("Please login first!", "warning")
        return redirect("/sign-in")
    portfolio_data = []

    # Get user's all portfolio transactions
    holdings = Portfolio.query.filter_by(user_id=user.id).all()

    #initiate dictionary for storing all data
    coin_data ={}
    for holding in holdings:
        symbol = holding.co_symbol
        #add values for each coin first time in loop as dictionary in dictionary
        if symbol not in coin_data:
            coin_data[symbol] = {
                "total_quantity": 0,
                "total_paid": 0,
            }
        coin_data[symbol]["total_quantity"] += holding.quantity
        coin_data[symbol]["total_paid"] += holding.total_paid

    #initiate list for storing final data
    portfolio_data = []

    for symbol, data in coin_data.items():

        current_coin = Coin.query.filter_by(symbol=symbol).first()
        if current_coin:
            avg_buy_price = data["total_paid"] / data["total_quantity"]
            current_value = data["total_quantity"] * current_coin.price
            profit_loss = current_value - data["total_paid"]
            total_quantity = data["total_quantity"]
            portfolio_data.append({
                "co_symbol": symbol,
                "avg_buy_price": avg_buy_price,
                "price": current_coin.price,
                "profit_loss": profit_loss,
                "value": current_value,
                "quantity": total_quantity,
            })

    theads = ["Coin", "buy price", "price", "profit/loss", "value", "quantity"]
    return render_template("portfolio.html", theads = theads, username=user.username, session_token=session_token, portfolio=portfolio_data)

@app.route("/sign-in" , methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("input_email")
        password = request.form.get("input_password")

        # find user by email
        user = Ptracker.query.filter_by(email=email).first()

        # check if mail exist and pass is correct
        if user and user.password == password:

            # create session token and store it in DB
            session_token = str(uuid.uuid4())
            user.session_token = session_token
            db.session.commit()

            # create response with redirect
            response = make_response(redirect("/portfolio"))

            # set cookie
            response.set_cookie("session_token", session_token , httponly=True, samesite="strict", max_age=60*60*24*365 )
            flash("login successful!", "success")
            return response
        else:
            # one generic message for both fields for better safety
            flash("  Email or password is invalid!", "danger")
            return render_template("signin.html")

    return render_template("signin.html")

@app.route("/sign-up" , methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("input_username")
        email = request.form.get("input_email")
        password = request.form.get("input_password")
        confirm = request.form.get("confirm_password")
        print("{0} : {1} : {2} : {3} ".format(username, email, password, confirm))

        # 1. Check if all fields are filled
        if not username or not email or not password or not confirm:
            flash("  All fields are required!", "danger")
            return render_template("signup.html")

        # 2. Check if passwords match
        elif password != confirm:
            flash("  Passwords don't match!", "danger")
            return render_template("signup.html")

        # 3. Check if username already exists
        elif Ptracker.query.filter_by(username=username).first():
            flash("  Username already taken!", "danger")
            return render_template("signup.html")

        # 4. Check if email already exists
        elif Ptracker.query.filter_by(email=email).first():
            flash("  Email already registered!", "danger")
            return render_template("signup.html")
        else:
            ptracker = Ptracker(username=username, email=email, password=password)
            db.session.add(ptracker)
            db.session.commit()
            flash("Account created successfully! You can sign in.", "success")
            return redirect("/sign-in")
    return render_template("signup.html")

@app.route("/sign-out")
def sign_out():

    # Get session_token from cookie
    session_token = request.cookies.get("session_token")

    # remove session_token from DB
    user = Ptracker.query.filter_by(session_token=session_token).first()
    if user:
        user.session_token = None
        db.session.commit()

    # create response with redirect
    response = make_response(redirect("/"))

    # delete cookie and redirect on index
    response.delete_cookie("session_token")
    flash("Sign out successful!", "success")
    return response

@app.route("/add-coin", methods=["GET", "POST"])
def add_coin():

    # Get session_token from cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        flash("Please login first!", "warning")
        return redirect("/sign-in")
    user = Ptracker.query.filter_by(session_token=session_token).first()
    if not user:
        flash("Please login first!", "warning")
        return redirect("/sign-in")

    # get all coins from DB for dropdown
    available_coins = Coin.query.order_by(Coin.rank).all()

    if request.method == "POST":
        coin_symbol = request.form.get("coin_symbol")
        quantity = request.form.get("quantity")
        total_paid = request.form.get("total_paid")

        # double check if fields are filled
        if not coin_symbol or not quantity or not total_paid:
            flash("All fields are required!", "danger")
            return render_template("addcoin.html", username=user.username, coins=available_coins)

        coin_symbol = coin_symbol.upper().strip()

        try:
            quantity = float(quantity)
            total_paid = float(total_paid)

            # check if both are positive numbers
            if quantity <= 0:
                flash("Quantity must be greater than zero!", "danger")
                return render_template("addcoin.html", username=user.username, coins=available_coins)

            if total_paid <= 0:
                flash("Total paid must be greater than zero!", "danger")
                return render_template("addcoin.html", username=user.username, coins=available_coins)

        except ValueError:
            flash("Please enter valid numbers!", "danger")
            return render_template("addcoin.html", username=user.username, coins=available_coins)

        # double check if coin exists in database
        coin = Coin.query.filter_by(symbol=coin_symbol).first()

        if not coin:
            flash(f"Coin {coin_symbol} not found in our database!", "danger")
            return render_template("addcoin.html", username=user.username, coins=available_coins)

        # Add to portfolio and save to DB
        new_holding = Portfolio(
            user_id=user.id,
            co_symbol=coin_symbol,
            co_name=coin.name,
            quantity=quantity,
            total_paid=total_paid
        )
        db.session.add(new_holding)
        db.session.commit()

        # Calculate price per coin for display
        price_per_coin = total_paid / quantity

        # Check which button was clicked
        action = request.form.get("action")

        if action == "Sub_and_add":
            flash(f"Added {quantity} {coin_symbol} (${price_per_coin:,.2f}/coin)! Add another transaction.", "success")
            return render_template("addcoin.html", username=user.username, coins=available_coins)
        else:
            flash(f"Successfully added {quantity} {coin_symbol} to your portfolio!", "success")
            return redirect("/portfolio")

    return render_template("addcoin.html", coins = available_coins)

if __name__ == "__main__":
    app.run(debug=True)