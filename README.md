<h1 align="center">
Stock Assets API
</h1>

<p align="center">
<a href="https://stock-assets.herokuapp.com/assets">Stock Assets API</a>
</p>

<p align="center">
This is API contains data of the following stock/cryptocurrency tickers: "BYND", "DIS", "MSFT", "NFLX", "ROKU", "UAL", "ZM", "TSLA", "BTC". API is automated to refresh every 30 seconds. Built with python libraries and frameworks.
</p>

## Setup
### Clone directory:
```
$ cd [workspace folder]
$ git clone https://stock-assets.herokuapp.com/assets
```

### Create Python virtual environment:
```
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

### Setup database and populate:
```
(venv) $ createdb assets-portfolio
(venv) $ python seed.py
```

### Start server:
```
(venv) $ flask run
```
Open http://localhost:5000/assets to view project in the browser.

## Built With
* [Pandas](https://pandas.pydata.org/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
* [PostgresSQL](https://www.postgresql.org/)

## Authors
* Kevin Reber - [Github](https://github.com/kevinreber) - [Website](https://www.kevinreber.dev/) - [LinkedIn](https://www.linkedin.com/in/kevin-reber-6a663860/)

## Hosted on 
[Heroku](https://www.heroku.com/)