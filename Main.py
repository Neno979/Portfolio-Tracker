from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = ("sqlite:///sqlite.db")
db = SQLAlchemy(app)

class Ptracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    confirm = db.Column(db.String, unique=True)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    headers = ["#", "Price", "M.Cap.", "24hVol.", "24h%"]
    return render_template("index.html", headers = headers)

@app.route("/portfolio" , methods=["GET", "POST"])
def portfolio():
    headers = ["Coin","share", "profit", "value", "size", "ma 7d"]
    return render_template("portfolio.html", headers = headers)

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