from datetime import datetime

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from fyyur import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Show = db.Table('Show',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('start_time', db.DateTime, nullable=False)
)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))  # tried many to many with a Genre table, but this seemed like a better option.

    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))

    phone = db.Column(db.String(120))

    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))

    venues = db.relationship('Artist', secondary=Show, backref=db.backref('venues', lazy='joined'))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    genres = db.Column(db.ARRAY(db.String))

    city = db.Column(db.String(120))
    state = db.Column(db.String(120))

    phone = db.Column(db.String(120))

    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))

    # TODO DONE: implement any missing fields, as a database migration using Flask-Migrate

# TODO DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Queries.
#----------------------------------------------------------------------------#

def upcoming_shows_for_venue(venue_id) -> int:
    """
    Count the number of upcoming shows for given venue.
    """
    return db.session.query(func.count(Show.c.venue_id)) \
        .filter(Show.c.venue_id == venue_id) \
        .filter(Show.c.start_time > datetime.now()).scalar()


def upcoming_shows_for_artist(artist_id):
    """
    Count the number of upcoming shows for given artist.
    """
    return db.session.query(func.count(Show.c.artist_id)) \
        .filter(Show.c.artist_id == artist_id) \
        .filter(Show.c.start_time > datetime.now()).scalar()
