from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    headers = ["#", "Coin", "Price", "M.Cap.", "24hVol.", "24h%"]
    return render_template('index.html', headers = headers)

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')
if __name__ == '__main__':
    app.run(debug=True)