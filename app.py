from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from models import db, connect_db, Stock
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
from dotenv import load_dotenv
import pandas
import numpy as np
from datetime import datetime, timedelta
from config import DevelopmentConfig
import schedule
import time


# load environment variables
load_dotenv()

app = Flask(__name__)
api = Api(app)

app.config.from_object("config.DevelopmentConfig")
# debug = DebugToolbarExtension(app)

connect_db(app)

TODAY = str(datetime.now().strftime('%Y-%m-%d'))
DAILY = str((datetime.now() - timedelta(2)).strftime('%Y-%m-%d'))
WEEKLY = str((datetime.now() - timedelta(7)).strftime('%Y-%m-%d'))
ANNUAL = str((datetime.now() - timedelta(365)).strftime('%Y-%m-%d'))

TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND", "TSLA"]


class Assets(Resource):
    def get(self):
        """Return response of assets to user."""

        tickers = Stock.query.all()

        # Store all prices of stocks
        stocks = {t: get_stock(t) for t in tickers}
        data = stocks
        return (data, 201)


def get_stock(ticker):

    stock = Stock.query.get_or_404(ticker)

    changes = {
        "daily": stock.daily_perc_change,
        "weekly": stock.weekly_perc_change,
        "annual": stock.annual_perc_change
    }

    price_data = {
        "price": stock.price,
        "dailyPriceChange": stock.dailyPriceChange,
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
    Returns price of ticker symbol.

    get_data() will return a nested dict of the ticker symbols's dataframe.
    Storing the tickers's ["Close"] key will give us the closing price of the stock.

    ex:
        get_data(USA_STOCK)["Close"]

    will return:
        [Timestamp('2020-05-29 00:00:00'), 2442.3701171875]
    """

    stock = Stock.query.get(ticker)

    today_price = get_data(ticker, TODAY, TODAY)["Close"][1]
    daily_price = get_data(ticker, DAILY, TODAY)["Close"][1]
    weekly_price = get_data(ticker, WEEKLY, TODAY)["Close"][1]
    annual_price = get_data(ticker, ANNUAL, TODAY)["Close"][1]

    if not stock:
        stock = Stock(ticker=ticker,
                      price=float(today_price - daily_price),
                      daily_price_change=percent_change(
                          today_price, daily_price),
                      daily_perc_change=percent_change(
                          today_price, daily_price),
                      weekly_perc_change=percent_change(
                          today_price, weekly_price),
                      annual_perc_change=percent_change(
                          today_price, annual_price)
                      )
        db.session.add(stock)

    else:
        stock.price = today_price
        stock.daily_price_change = float(today_price - daily_price)
        stock.daily_perc_change = percent_change(today_price, daily_price)
        stock.weekly_perc_change = percent_change(today_price, weekly_price)
        stock.annual_perc_change = percent_change(today_price, annual_price)

    db.session.commit()


def update_db():
    """Updates all tickers every 30 seconds"""

    for t in TICKER_SYMBOLS:
        update_prices(t)


def print_this():
    print("hello world")


@app.route("/")
def home():
    """Empty"""

    schedule.every(30).seconds.do(update_db())

    while 1:
        schedule.run_pending()
        time.sleep(1)

    return 'Hello World!'


# @app.route('/assets', methods=['GET'])
# def get_assets():
#     """Return response of assets to user."""

#     # Store all prices of stocks
#     stocks = {t: get_prices(t) for t in TICKER_SYMBOLS}

#     return (jsonify(stocks=stocks), 201)
