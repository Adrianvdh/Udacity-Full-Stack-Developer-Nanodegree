#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging

from sqlalchemy import func

from forms import *

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form
from logging import Formatter, FileHandler
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO DONE: connect to a local postgresql database

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
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

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


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # Problem solving steps:
  # 1. Query the venues by state and city using group by.
  # 2. For each state and city pair in the above result set, query all venues matching that state and city.
  # 3. For each venue, aggregate the number of upcoming shows where the start date is greater
  #    than the present date.

  venues_states_and_cities = db.session.query(Venue.state, Venue.city)\
    .group_by(Venue.state, Venue.city)\
    .order_by(Venue.state, Venue.city).all()

  results = []

  for state, city in venues_states_and_cities:
    venues_matching_in_state_and_city = Venue.query.filter_by(state=state, city=city).all()
    result_dict = {
      'city': city,
      'state': state,
      'venues': []
    }

    for venue in venues_matching_in_state_and_city:
      result_dict['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': upcoming_shows_for_venue(venue.id)
      })

    results.append(result_dict)

  return render_template('pages/venues.html', areas=results)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Problem solving steps:
  # 1. Get all results matching the search string.
  # 2. Count the number of results
  # 3. For each result, calculate the number of shows

  search_term = request.form.get('search_term', '')

  matchng_venues_q = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  matching_venues = matchng_venues_q.all()
  matching_venues_count = matchng_venues_q.count()

  response = {
    "count": matching_venues_count,
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_shows_for_venue(venue.id),
    } for venue in matching_venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: DONE replace with real venue data from the venues table, using venue_id

  def query_past_or_upcoming_shows(venue_id, upcoming=True):
    q = db.session.query(
      Artist.id.label('artist_id'),
      Artist.name.label('artist_name'),
      Artist.image_link.label('artist_image_link'),
      Show.c.start_time.label('start_time'),
    ).filter(Show.c.venue_id == venue_id) \
     .filter(Show.c.artist_id == Artist.id)

    if upcoming:
      return q.filter(Show.c.start_time > datetime.now())
    else:
      return q.filter(Show.c.start_time < datetime.now())

  def create_shows_dict(show: Show) -> dict:
    return {
      'artist_id': show.artist_id,
      'artist_name': show.artist_name,
      'artist_image_link': show.artist_image_link,
      'start_time': str(show.start_time)
    }

  venue = Venue.query.get(venue_id)
  response = {**vars(venue)}

  past_shows_q = query_past_or_upcoming_shows(venue.id, upcoming=False)
  upcoming_shows_q = query_past_or_upcoming_shows(venue.id, upcoming=True)

  response['past_shows'] = [create_shows_dict(show) for show in past_shows_q.all()]
  response['past_shows_count'] = past_shows_q.count()
  response['upcoming_shows'] = [create_shows_dict(show) for show in upcoming_shows_q.all()]
  response['upcoming_shows_count'] = upcoming_shows_q.count()

  return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO DONE: insert form data as a new Venue record in the db, instead
  # TODO DONE: modify data to be the data object returned from db insertion

  form = VenueForm(request.form)

  if form.validate_on_submit():
    try:
      venue = Venue(
        name=form.data.get('name'),
        genres=form.data.get('genres'),
        city=form.data.get('city'),
        state=form.data.get('state'),
        address=form.data.get('address'),
        phone=form.data.get('phone'),
        website=form.data.get('website'),
        facebook_link=form.data.get('facebook_link')
      )
      db.session.add(venue)
      db.session.commit()
      flash('The venue "' + request.form['name'] + '", was successfully listed!', 'alert-primary')
    except Exception as e:
      flash('An error occurred when saving the venue. The venue "' + form.data.get('name') + '", could not be listed.',
            'alert-danger')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    # TODO DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred when submitting this form. Venue ' + form.data.get('name') + ' could not be listed.',
          'alert-danger')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE DONE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # See: show_venue.html

  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The venue "' + venue.name + '", was successfully deleted!', 'alert-primary')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO DONE: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # Problem solving steps:
  # 1. Get all results matching the search string.
  # 2. Count the number of results
  # 3. For each result, calculate the number of shows

  search_term = request.form.get('search_term', '')

  matchng_artists_q = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  matching_artists = matchng_artists_q.all()
  matching_artists_count = matchng_artists_q.count()

  response={
    "count": matching_artists_count,
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcoming_shows_for_artist(artist.id),
    } for artist in matching_artists]
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO DONE: replace with real venue data from the venues table, using artist_id

  def query_past_or_upcoming_shows(artist_id, upcoming=True):
    q = db.session.query(
      Venue.id.label('venue_id'),
      Venue.name.label('venue_name'),
      Venue.image_link.label('venue_image_link'),
      Show.c.start_time.label('start_time'),
    ).filter(Show.c.artist_id == artist_id) \
      .filter(Show.c.venue_id == Venue.id)

    if upcoming:
      return q.filter(Show.c.start_time > datetime.now())
    else:
      return q.filter(Show.c.start_time < datetime.now())

  def create_shows_dict(show: Show) -> dict:
    return {
      'venue_id': show.venue_id,
      'venue_name': show.venue_name,
      'venue_image_link': show.venue_image_link,
      'start_time': str(show.start_time)
    }

  artist = Artist.query.get(artist_id)
  response = {**vars(artist)}

  past_shows_q = query_past_or_upcoming_shows(artist.id, upcoming=False)
  upcoming_shows_q = query_past_or_upcoming_shows(artist.id, upcoming=True)

  response['past_shows'] = [create_shows_dict(show) for show in past_shows_q.all()]
  response['past_shows_count'] = past_shows_q.count()
  response['upcoming_shows'] = [create_shows_dict(show) for show in upcoming_shows_q.all()]
  response['upcoming_shows_count'] = upcoming_shows_q.count()

  return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  form = ArtistForm(obj=artist)

  # TODO DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)

  if form.validate_on_submit():
    try:
      artist = Artist.query.get(artist_id)
      artist.name = form.data.get('name'),
      artist.city = form.data.get('city'),
      artist.state = form.data.get('state'),
      artist.phone = form.data.get('phone'),
      artist.genres = list([genre for genre in form.data.get('genres')])
      artist.facebook_link = form.data.get('facebook_link')

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.data.get('name') + ' was successfully updated!', 'alert-primary')
    except Exception as e:
      e.print_exc()
      db.session.rollback()
    finally:
      db.session.close()
  else:
    flash('An error occurred when submitting this form. Artist ' + form.data.get('name') + ' could not be updated.',
          'alert-danger')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)

  form = VenueForm(obj=venue)

  # TODO DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)

  if form.validate_on_submit():
    try:
      venue = Venue.query.get(venue_id)
      venue.name = form.data.get('name'),
      venue.city = form.data.get('city'),
      venue.state = form.data.get('state'),
      venue.address = form.data.get('address'),
      venue.phone = form.data.get('phone'),
      venue.genres = list([genre for genre in form.data.get('genres')])
      venue.facebook_link = form.data.get('facebook_link')

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + form.data.get('name') + ' was successfully updated!', 'alert-primary')
    except Exception as e:
      e.print_exc()
      db.session.rollback()
    finally:
      db.session.close()
  else:
    flash('An error occurred when submitting this form. Venue ' + form.data.get('name') + ' could not be updated.',
          'alert-danger')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO DONE: insert form data as a new Artist record in the db, instead
  # TODO DONE: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)

  if form.validate_on_submit():
    try:
      artist = Artist(
        name=form.data.get('name'),
        genres=form.data.get('genres'),
        city=form.data.get('city'),
        state=form.data.get('state'),
        phone=form.data.get('phone'),
        facebook_link=form.data.get('facebook_link')
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!', 'alert-primary')
    except Exception as e:
      flash('An error occurred when saving the artist. Artist ' + form.data.get('name') + ' could not be listed.',
            'alert-danger')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    # TODO DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred when submitting this form. Artist ' + form.data.get('name') + ' could not be listed.',
          'alert-danger')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  """
  select v.id as venue_id, v.name as venue_name, a.id as artist_id, a.name as artist_name, s.start_time as start_time
  from "Venue" v
  inner join "Show" s
  on s.venue_id = v.id
  inner join "Artist" a
  on s.artist_id = a.id
  order by s.start_time;
  """

  shows = db.session.query(
    Venue.id.label('venue_id'),
    Venue.name.label('venue_name'),
    Artist.id.label('artist_id'),
    Artist.name.label('artist_name'),
    Artist.image_link.label('artist_image_link'),
    Show.c.start_time.label('start_time'),
  ).filter(Show.c.venue_id == Venue.id) \
   .filter(Show.c.artist_id == Artist.id).all()

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO DONE: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)

  if form.validate_on_submit():
    try:
      show = Show.insert().values(
        artist_id=form.data.get('artist_id'),
        venue_id=form.data.get('venue_id'),
        start_time=form.data.get('start_time')
      )
      db.engine.execute(show)
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception as e:
      flash('An error occurred when saving the show. Show could not be listed.',
            'alert-danger')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    # TODO DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred when submitting this form. Show could not be listed.',
          'alert-danger')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
