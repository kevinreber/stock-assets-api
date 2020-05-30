import os
from dotenv import load_dotenv
load_dotenv()


class BaseConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # DEBUG TOOLBAR
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # SQL ALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql:///assets-portfolio')
    DEBUG_TB_ENABLED = False
