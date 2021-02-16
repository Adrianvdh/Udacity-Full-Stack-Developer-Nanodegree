import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# TODO DONE: connect to a local postgresql database

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://adrian@localhost:5432/udacity_fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
