import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Stock(db.Model):
    """Stock Model"""

    __tablename__ = "stocks"

    ticker = db.Column(db.String, primary_key=True, nullable=False)
    price = db.Column(db.String, nullable=False)
    daily_price_change = db.Column(db.String, nullable=False)
    daily_perc_change = db.Column(db.Integer, nullable=False)
    weekly_perc_change = db.Column(db.Integer, nullable=False)
    monthly_perc_change = db.Column(db.Integer, nullable=False)
