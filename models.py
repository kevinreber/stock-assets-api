import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Asset(db.Model):
    """Asset Model"""

    __tablename__ = "assets"

    id = db.Column(db.String, primary_key=True, nullable=False)
    asset = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    daily_price_change = db.Column(db.Float, nullable=False)
    daily_perc_change = db.Column(db.Float, nullable=False)
    weekly_perc_change = db.Column(db.Float)
    monthly_perc_change = db.Column(db.Float)
    annual_perc_change = db.Column(db.Float)
