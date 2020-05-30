from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from models import Stock
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
from dotenv import load_dotenv
import pandas
import numpy as np
from datetime import datetime, timedelta
from config import DevelopmentConfig

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

        # Store all prices of stocks
        stocks = {t: get_prices(t) for t in TICKER_SYMBOLS}
        data = stocks
        return (data, 201)


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


def get_prices(ticker):
    """
    Returns price of ticker symbol.

    get_data() will return a nested dict of the ticker symbols's dataframe.
    Storing the tickers's ["Close"] key will give us the closing price of the stock.

    ex:
        get_data(USA_STOCK)["Close"]

    will return:
        [Timestamp('2020-05-29 00:00:00'), 2442.3701171875]
    """

    stock = Stock.query.get_or404(ticker)

    today_price = get_data(ticker, TODAY, TODAY)["Close"][1]
    daily_price = get_data(ticker, DAILY, TODAY)["Close"][1]
    weekly_price = get_data(ticker, WEEKLY, TODAY)["Close"][1]
    annual_price = get_data(ticker, ANNUAL, TODAY)["Close"][1]

    stock.price = today_price
    stock.daily_price_change = float(today_price - daily_price)
    stock.daily_perc_change = percent_change(today_price, daily_price)
    stock.weekly_perc_change = percent_change(today_price, weekly_price)
    stock.annual_perc_change = percent_change(today_price, annual_price)

    db.session.commit()

    # changes = {
    #     "daily": percent_change(today_price, daily_price),
    #     "weekly": percent_change(today_price, weekly_price),
    #     "annual": percent_change(today_price, annual_price)
    # }

    # price_data = {
    #     "price": float(today_price),
    #     "dailyPriceChange": float(today_price - daily_price),
    #     "priceChangePercentages": changes
    # }

    # return price_data


@app.route("/")
def home():
    """Empty"""

    return 'Hello World!'


# @app.route('/assets', methods=['GET'])
# def get_assets():
#     """Return response of assets to user."""

#     # Store all prices of stocks
#     stocks = {t: get_prices(t) for t in TICKER_SYMBOLS}

#     return (jsonify(stocks=stocks), 201)


api.add_resource(Assets, "/assets")

if __name__ == '__main__':
    app.run()
