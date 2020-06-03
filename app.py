# Python standard libraries
from datetime import datetime, timedelta

# Third-party libraries
from flask import Flask, jsonify, request
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError
from dotenv import load_dotenv
from flask_cors import CORS
import pandas as pd
import numpy as np
from flask_apscheduler import APScheduler
from forex_python.bitcoin import BtcConverter

# Internal imports
from models import db, connect_db, Asset
from config import BaseConfig
from stock_tickers import TICKER_SYMBOLS

# Load environment variables
load_dotenv()

# Initializers
app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
b = BtcConverter()

app.config.from_object("config.BaseConfig")
connect_db(app)

#########################################################
# Stock Date time's
#########################################################
TODAY = str(datetime.now().strftime('%Y-%m-%d'))
DAILY = str((datetime.now() - timedelta(2)).strftime('%Y-%m-%d'))
WEEKLY = str((datetime.now() - timedelta(7)).strftime('%Y-%m-%d'))
MONTHLY = str((datetime.now() - timedelta(30)).strftime('%Y-%m-%d'))
ANNUAL = str((datetime.now() - timedelta(365)).strftime('%Y-%m-%d'))


#########################################################
# Handle Data Functions
#########################################################

def get_data(ticker, start, end):
    """Get ticker symbol's closing data from yahoo finance.

    If a date is missing price data, a KeyError will be thrown and 
    a FALL_BACK_DATE will handle the error and find the most recent 
    price data in the stock market.
    """

    FALL_BACK_DATE = str((datetime.now() - timedelta(5)).strftime('%Y-%m-%d'))

    try:
        # .DataReader() will return a dataframe
        stock_data = data.DataReader(ticker, 'yahoo', start, end)
        price = stock_data["Close"][0]

    except KeyError:
        print(f"Getting {ticker}'s' most recent price...")
        clean = clean_data(ticker, 'Close', FALL_BACK_DATE, end)
        print("most recent price is...")
        print(clean.tail(1)["Close"][0])
        price = clean.tail(1)["Close"][0]

    except RemoteDataError:
        print("No data found for {t}".format(t=ticker))

    return price


def update_prices(ticker):
    """Updates DB of price and price changes of ticker symbol."""

    today_price = float(get_data(ticker, TODAY, TODAY))
    daily_price = float(get_data(ticker, DAILY, TODAY))
    weekly_price = float(get_data(ticker, WEEKLY, TODAY))
    monthly_price = float(get_data(ticker, MONTHLY, TODAY))
    annual_price = float(get_data(ticker, ANNUAL, TODAY))

    stock = Asset.query.get(ticker)

    if stock:
        stock.price = today_price
        stock.daily_price_change = today_price - daily_price
        stock.daily_perc_change = percent_change(today_price, daily_price)
        stock.weekly_perc_change = percent_change(today_price, weekly_price)
        stock.monthly_perc_change = percent_change(today_price, monthly_price)
        stock.annual_perc_change = percent_change(today_price, annual_price)

    else:
        new_stock = Asset(id=ticker,
                          asset="stock",
                          price=today_price,
                          daily_price_change=today_price - daily_price,
                          daily_perc_change=percent_change(
                              today_price, daily_price),
                          weekly_perc_change=percent_change(
                              today_price, weekly_price),
                          monthly_perc_change=percent_change(
                              today_price, monthly_price),
                          annual_perc_change=percent_change(today_price, annual_price))
        db.session.add(new_stock)

    db.session.commit()
    print(f'{ticker} updated!')


#########################################################
# Helper Functions
#########################################################

def clean_data(ticker, col, start_date, end_date):
    """Cleans any missing days of the specified time frame"""

    print(f"cleaning....{start_date} and ${end_date}")
    weekdays = data.DataReader(ticker, 'yahoo', start_date, end_date)
    print(weekdays)
    print("done cleaning..")
    return weekdays.fillna(method='ffill')


def percent_change(current, start):
    """Returns percentage change"""

    return ((float(current)-start) / abs(start)) * 100


def serialize(asset):
    """Serializes data"""

    return {
        'prices': {
            'price': asset.price,
            'dailyChange': asset.daily_price_change,
        },
        'percentChanges': {
            'dailyChange': asset.daily_perc_change,
            'weeklyChange': asset.weekly_perc_change,
            'monthlyChange': asset.monthly_perc_change,
            'annualChange': asset.annual_perc_change
        }
    }


def update_db():
    """Updates all tickers"""

    update_crypto('BTC')
    for t in TICKER_SYMBOLS:
        update_prices(t)

    print("Finished updating assets")


#########################################################
# Crypto Variables and Date times
#########################################################
CRYPTO_DAILY = (datetime.now() - timedelta(2))
CRYPTO_WEEKLY = (datetime.now() - timedelta(7))
CRYPTO_MONTHLY = (datetime.now() - timedelta(30))
CRYPTO_ANNUAL = (datetime.now() - timedelta(365))

# .get_previous_price() only takes a date object
btc_price = b.get_latest_price('USD')
btc_daily_price = b.get_previous_price('USD', CRYPTO_DAILY)
btc_weekly_price = b.get_previous_price('USD', CRYPTO_WEEKLY)
btc_monthly_price = b.get_previous_price('USD', CRYPTO_MONTHLY)
btc_annual_price = b.get_previous_price('USD', CRYPTO_ANNUAL)


def update_crypto(crypto):
    """Add crypto data to database"""

    btc = Asset.query.get(crypto)

    if btc:
        btc.price = btc_price
        btc.daily_price_change = float(btc_price - btc_daily_price)
        btc.daily_perc_change = percent_change(btc_price, btc_daily_price)
        btc.weekly_perc_change = percent_change(btc_price, btc_weekly_price)
        btc.monthly_perc_change = percent_change(btc_price, btc_monthly_price)
        btc.annual_perc_change = percent_change(btc_price, btc_annual_price)
    else:
        new_btc = Asset(id=crypto,
                        asset="crypto",
                        price=btc_price,
                        daily_price_change=btc_price - btc_daily_price,
                        daily_perc_change=percent_change(
                            btc_price, btc_daily_price),
                        weekly_perc_change=percent_change(
                            btc_price, btc_weekly_price),
                        monthly_perc_change=percent_change(
                            btc_price, btc_monthly_price),
                        annual_perc_change=percent_change(btc_price, btc_annual_price))
        db.session.add(new_btc)

    db.session.commit()
    print(f'{crypto} updated!')

#########################################################
# Routes
#########################################################


@app.route("/")
def home():
    """Home Page, keep empty"""

    update_db()
    return 'Hello World!'


@app.route('/assets', methods=['GET'])
def get_assets():
    """Return response of assets to user."""

    stocks = Asset.query.filter(Asset.asset == "stock").all()
    cryptos = Asset.query.filter(Asset.asset == "crypto").all()

    ser_stocks = {s.id: serialize(s) for s in stocks}
    ser_cryptos = {c.id: serialize(c) for c in cryptos}

    assets = {
        'stocks': ser_stocks,
        'cryptos': ser_cryptos
    }

    return (jsonify(data=assets))


# Set schedule task to run every 30 seconds
if __name__ == "__main__":
    scheduler.add_job(id='Scheduled task', func=update_db,
                      trigger='interval', seconds=35)
    scheduler.start()
    app.run()
