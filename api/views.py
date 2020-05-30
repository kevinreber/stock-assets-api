from flask import Blueprint, jsonify, request
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# tsla = yf.Ticker("TSLA")


# Define assets Blueprint
assets = Blueprint('assets', __name__)

# import yfinance as yf

# START_DATE = '2020-5-20'
TODAY = str(datetime.now().strftime('%Y-%m-%d'))
DAILY = str((datetime.now() - timedelta(1)).strftime('%Y-%m-%d'))
WEEKLY = str((datetime.now() - timedelta(7)).strftime('%Y-%m-%d'))
ANNUAL = str((datetime.now() - timedelta(365)).strftime('%Y-%m-%d'))

TICKER_SYMBOLS = ["MSFT", "ZM", "UAL", "NFLX", "ROKU", "DIS", "BYND", "TSLA"]


def get_data(ticker, start, end):
    """Get ticker symbol's data from yahoo finance"""

    try:
        stock_data = data.DataReader(ticker, 'yahoo', start, end)

        # convert data frame to dictionary
        # return stock_data.to_dict()
        # return stock_data

        return(stock_data)

    except RemoteDataError:
        print("No data found for {t}".format(t=ticker))

# def get_stats(stock_data):
#     return {

#     }


def clean_data(stock_data, col):
    weekdays = pd.date_range(start=TODAY, end=TODAY)
    clean_data = stock_data[col].reindex(weekdays)
    return clean_data.fillna(method='ffill')


def get_price(ticker):
    """
    Return price of ticker symbol.

    get_data() will return a nested dict of the stock's dataframe.
    Storing the stock's ["Close"] key/value will give us the most recent price in the stock.

    ex:
        get_data(USA_STOCK)["Close"]

    will return:
        {Timestamp('2020-05-29 00:00:00'): 2442.3701171875}

    """

    price = round(list(get_data(ticker, TODAY, TODAY)["Close"].values())[0], 2)
    print(price)
    return price


@assets.route('/assets', methods=['GET'])
def get_assets():
    """Return response of assets to user."""

    data = request.get_json()

    # today_price = [get_data(t, TODAY, TODAY) for t in TICKER_SYMBOLS]
    # change_daily = [get_data(t, DAILY, TODAY) for t in TICKER_SYMBOLS]
    # change_weekly = [get_data(t, WEEKLY, TODAY) for t in TICKER_SYMBOLS]
    # change_annual = [get_data(t, ANNUAL, TODAY) for t in TICKER_SYMBOLS]

    # print(today_price, daily_weekly, change_weekly, annual_weekly)

    # Store all prices of stocks
    stocks = {t: get_price(t) for t in TICKER_SYMBOLS}

    return stocks
