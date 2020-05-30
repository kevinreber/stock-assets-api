<h1 align="center">
Stock Assets API
</h1>

<p align="center">
<a href="https://stock-assets.herokuapp.com/assets">Stock Assets API</a>
</p>

<p align="center">
This is API contains data of the following stock tickers: "BYND", "DIS", "MSFT", "NFLX", "ROKU", "UAL", "ZM". API is automated to refresh every 30 seconds. No external API's were used, everything was built using python libraries.
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
Open http://localhost:5000/ to view project in the browser.

## Hosted on 
[Heroku](https://www.heroku.com/)