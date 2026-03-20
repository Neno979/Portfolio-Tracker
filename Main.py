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
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    session_token = db.Column(db.String, unique=True)

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True)
    name = db.Column(db.String, unique=True)
    symbol = db.Column(db.String, unique=True)
    price = db.Column(db.Float, unique=False)
    mcap = db.Column(db.Float, unique=False)
    volume = db.Column(db.Float, unique=False)
    change = db.Column(db.Float, unique=False)

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

    return render_template("index.html", theads = theads, coins = coins)

@app.route("/portfolio" , methods=["GET", "POST"])
def portfolio():
    session_token = request.cookies.get("session_token")
    if not session_token:
        flash("Please login first!", "warning")
        return redirect("/login")
    user = Ptracker.query.filter_by(session_token=session_token).first()
    if not user:
        flash("Please login first!", "warning")
        return redirect("/login")

    theads = ["Coin","share", "profit", "value", "size", "ma 7d"]
    return render_template("portfolio.html", theads = theads)

@app.route("/sign-in" , methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("input_email")
        password = request.form.get("input_password")

        # find user by email
        user = Ptracker.query.filter_by(email=email).first()

        # check if mail exist and pass is correct
        if user and user.password == password:

            #create token and store it
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
            # one generic message for better safety
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

if __name__ == "__main__":
    app.run(debug=True)