from flask import Flask, jsonify, request
from models import db, connect_db, Stock
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
from dotenv import load_dotenv
from flask_cors import CORS
import pandas
import numpy as np
from datetime import datetime, timedelta
from config import BaseConfig
from flask_apscheduler import APScheduler
import schedule
import time
import json


# load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()

app.config.from_object("config.BaseConfig")

connect_db(app)

TODAY = str(datetime.now().strftime('%Y-%m-%d'))
DAILY = str((datetime.now() - timedelta(2)).strftime('%Y-%m-%d'))
WEEKLY = str((datetime.now() - timedelta(7)).strftime('%Y-%m-%d'))
ANNUAL = str((datetime.now() - timedelta(365)).strftime('%Y-%m-%d'))

# TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND", "TSLA"]
TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND"]


def get_stock(ticker):
    """Get stock from DB"""

    stock = Stock.query.get(ticker)

    changes = {
        "daily": stock.daily_perc_change,
        "weekly": stock.weekly_perc_change,
        "annual": stock.annual_perc_change
    }

    price_data = {
        "price": stock.price,
        "dailyPriceChange": stock.daily_price_change,
        "priceChangePercentages": changes
    }

    return price_data


def get_data(ticker, start, end):
    """Get ticker symbol's data from yahoo finance"""

    try:
        stock_data = data.DataReader(ticker, 'yahoo', start, end)

        return stock_data

    except RemoteDataError:
        print("No data found for {t}".format(t=ticker))


def percent_change(current, start):
    """Returns percentage change"""

    return ((float(current)-start) / abs(start)) * 100


def update_prices(ticker):
    """
    Returns price and price changes of ticker symbol.

    get_data() will return a nested dict of the ticker symbols's dataframe.
    Storing the tickers's ["Close"] key will give us the closing price of the stock.

    ex:
        get_data(USA_STOCK)["Close"]

    will return:
        [Timestamp('2020-05-29 00:00:00'), 2442.3701171875]
    """

    today_price = get_data(ticker, TODAY, TODAY)["Close"][0]
    daily_price = get_data(ticker, DAILY, TODAY)["Close"][0]
    weekly_price = get_data(ticker, WEEKLY, TODAY)["Close"][0]
    annual_price = get_data(ticker, ANNUAL, TODAY)["Close"][0]

    stock = Stock.query.get(ticker)

    if stock:
        stock.price = today_price
        stock.daily_price_change = float(today_price - daily_price)
        stock.daily_perc_change = percent_change(today_price, daily_price)
        stock.weekly_perc_change = percent_change(today_price, weekly_price)
        stock.annual_perc_change = percent_change(today_price, annual_price)

    else:
        new_stock = Stock(id=ticker,
                          price=today_price,
                          daily_price_change=today_price - daily_price,
                          daily_perc_change=percent_change(
                              today_price, daily_price),
                          weekly_perc_change=percent_change(
                              today_price, weekly_price),
                          annual_perc_change=percent_change(today_price, annual_price))
        db.session.add(new_stock)

    db.session.commit()
    print(f'{ticker} updated!')


def update_db():
    """Updates all tickers"""

    for t in TICKER_SYMBOLS:
        update_prices(t)


@app.route("/")
def home():
    """Home Page, keep empty"""

    update_db()
    return 'Hello World!'


@app.route('/assets', methods=['GET'])
def get_assets():
    """Return response of assets to user."""

    stocks = Stock.query.all()
    ser_stocks = {s.id: serialize(s) for s in stocks}

    return (jsonify(data=ser_stocks))


def serialize(s):
    """Serializes data"""

    return {
        'prices': {
            'price': s.price,
            'dailyChange': s.daily_price_change,
        },
        'percentChanges': {
            'dailyChange': s.daily_perc_change,
            'weeklyChange': s.weekly_perc_change,
            'annualChange': s.annual_perc_change
        }
    }


# Set schedule task to run every 30 seconds
if __name__ == "__main__":
    scheduler.add_job(id='Scheduled task', func=update_db,
                      trigger='interval', seconds=30)
    scheduler.start()
    app.run()
