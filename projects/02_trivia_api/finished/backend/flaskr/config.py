import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# TODO DONE: connect to a local postgresql database

# Connect to the database
DB_USER = os.environ.get('DB_USER', 'adrian')
DB_PASSWORD = os.environ.get('DB_PASSWORD', None)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_POST = os.environ.get('DB_POST', 5432)
DB_NAME = os.environ.get('DB_NAME', 'udacity_trivia')


def build_url():
    result = 'postgresql://'
    result += DB_USER
    if DB_PASSWORD:
        result += f':{DB_PASSWORD}'
    result += f'@{DB_HOST}'
    result += f':{DB_POST}'
    result += f'/{DB_NAME}'
    return result


SQLALCHEMY_DATABASE_URI = build_url()
SQLALCHEMY_TRACK_MODIFICATIONS = False
