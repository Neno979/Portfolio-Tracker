from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"
db = SQLAlchemy(app)

class Ptracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    confirm = db.Column(db.String, unique=True)

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True)
    name = db.Column(db.String, unique=True)
    price = db.Column(db.Float, unique=False)
    mcap = db.Column(db.Float, unique=False)
    volume = db.Column(db.Float, unique=False)
    change = db.Column(db.Float, unique=False)


with app.app_context():
    db.create_all()

@app.route("/")
def index():
    theads = ["#", "Price", "M.Cap.", "24hVol.", "24h%"]
    API_KEY = "coinranking6ae704e6e7974096325d95be12cd9c383994de673acb79bf"
    url = "https://api.coinranking.com/v2/coin/Qwsogvtv82FCd"
    headers = {"x-access-token": API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    bitcoin_data = data['data']['coin']
    btc = Coin.query.filter_by(name='Bitcoin').first()

    if btc:
        btc.price = float(bitcoin_data['price'])
        btc.mcap = float(bitcoin_data['marketCap'])
        btc.volume = float(bitcoin_data['24hVolume'])
        btc.change = float(bitcoin_data['change'])
    else:
        btc = Coin(
            rank=1,
            name=bitcoin_data['name'],
            price=float(bitcoin_data['price']),
            mcap=float(bitcoin_data['marketCap']),
            volume=float(bitcoin_data['24hVolume']),
            change=float(bitcoin_data['change'])
        )
        db.session.add(btc)

    db.session.commit()

    return render_template("index.html", headers = headers, theads = theads, btc = btc)

@app.route("/portfolio" , methods=["GET", "POST"])
def portfolio():
    theads = ["Coin","share", "profit", "value", "size", "ma 7d"]
    return render_template("portfolio.html", theads = theads)

@app.route("/sign-in" , methods=["GET", "POST"])
def sign_in():
    return render_template("signin.html")

@app.route("/sign-up" , methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("input_username")
        email = request.form.get("input_email")
        password = request.form.get("input_password")
        confirm = request.form.get("confirm_password")
        print("{0} : {1} : {2} : {3} ".format(username, email, password, confirm))
        ptracker = Ptracker(username=username, email=email, password=password, confirm = confirm)
        db.session.add(ptracker)
        db.session.commit()
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)