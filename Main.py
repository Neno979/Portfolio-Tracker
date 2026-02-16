from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def index():
    headers = ["#", "Coin", "Price", "M.Cap.", "24hVol.", "24h%"]
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
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)