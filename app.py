from flask import Flask, jsonify, request
# from flask_restful import Resource, Api
from models import db, connect_db, Stock
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
from dotenv import load_dotenv
import pandas
import numpy as np
from datetime import datetime, timedelta
from config import DevelopmentConfig
from flask_apscheduler import APScheduler
import schedule
import time
import json


# load environment variables
load_dotenv()

app = Flask(__name__)
scheduler = APScheduler()
# api = Api(app)

app.config.from_object("config.DevelopmentConfig")
# debug = DebugToolbarExtension(app)

connect_db(app)

TODAY = str(datetime.now().strftime('%Y-%m-%d'))
DAILY = str((datetime.now() - timedelta(2)).strftime('%Y-%m-%d'))
WEEKLY = str((datetime.now() - timedelta(7)).strftime('%Y-%m-%d'))
ANNUAL = str((datetime.now() - timedelta(365)).strftime('%Y-%m-%d'))

# TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND", "TSLA"]
TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND"]


# class Assets(Resource):
#     def get(self):
#         """Return response of assets to user."""

#         tickers = Stock.query.all()

#         # Store all prices of stocks
#         stocks = {t: get_stock(t) for t in tickers}
#         data = stocks
#         return (data, 201)


def get_stock(ticker):

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
    Returns price of ticker symbol.

    get_data() will return a nested dict of the ticker symbols's dataframe.
    Storing the tickers's ["Close"] key will give us the closing price of the stock.

    ex:
        get_data(USA_STOCK)["Close"]

    will return:
        [Timestamp('2020-05-29 00:00:00'), 2442.3701171875]
    """
    print(get_data(ticker, TODAY, TODAY))
    today_price = get_data(ticker, TODAY, TODAY)["Close"][0]
    daily_price = get_data(ticker, DAILY, TODAY)["Close"][0]
    weekly_price = get_data(ticker, WEEKLY, TODAY)["Close"][0]
    annual_price = get_data(ticker, ANNUAL, TODAY)["Close"][0]

    stock = Stock.query.get(ticker)

    if stock:
        print('updating....')

        stock.price = today_price
        stock.daily_price_change = float(today_price - daily_price)
        stock.daily_perc_change = percent_change(today_price, daily_price)
        stock.weekly_perc_change = percent_change(today_price, weekly_price)
        stock.annual_perc_change = percent_change(today_price, annual_price)
        print(stock)

        print('updated!')

    else:
        print('new stock....')
        new_stock = Stock(id=ticker,
                          price=today_price,
                          daily_price_change=today_price - daily_price,
                          daily_perc_change=percent_change(
                              today_price, daily_price),
                          weekly_perc_change=percent_change(
                              today_price, weekly_price),
                          annual_perc_change=percent_change(today_price, annual_price))
        db.session.add(new_stock)
        print(new_stock)
        print('added!')

    db.session.commit()
    print(f'{ticker} updated!')


def update_db():
    """Updates all tickers"""
    print('scheduled starting....')
    for t in TICKER_SYMBOLS:
        update_prices(t)


@app.route("/")
def home():
    """Empty"""

    # schedule.every(45).seconds.do(update_db())

    # while 1:
    #     schedule.run_pending()
    #     time.sleep(1)

    update_db()
    return 'Hello World!'


@app.route('/assets', methods=['GET'])
def get_assets():
    """Return response of assets to user."""

    stocks = Stock.query.all()

    print(stocks)
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


if __name__ == "__main__":
    scheduler.add_job(id='Scheduled task', func=update_db,
                      trigger='interval', seconds=45)
    scheduler.start()
    app.run()
