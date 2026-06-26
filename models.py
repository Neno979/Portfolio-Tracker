
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ptracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    session_token = db.Column(db.String, unique=True, nullable=True)
    is_deleted = db.Column(db.Boolean, unique=False, default=False)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ptracker.id'), nullable=False)
    co_symbol = db.Column(db.String, unique=False, nullable=False)
    co_name = db.Column(db.String, unique=False, nullable=False)
    quantity = db.Column(db.Float, unique=False, nullable=False)
    total_paid = db.Column(db.Float, unique=False, nullable=False)
    user = db.relationship('Ptracker', backref=db.backref('portfolio', lazy=True))

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    symbol = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    mcap = db.Column(db.Float, unique=False, nullable=False)
    volume = db.Column(db.Float, unique=False, nullable=False)
    change = db.Column(db.Float, unique=False, nullable=False)

    def format_value(self, value):
        if value >= 100_000_000_000:
            return f"{value / 1_000_000_000_000:.2f}T"
        elif value >= 100_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 100_000:
            return f"{value / 1_000_000:.2f}M"
        if value >= 100:
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
