#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.sql import func
import datetime
import sys
#from models import Show, Venue, Artist, Genre, venue_genre_association, artist_genre_association
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

# Models.
#----------------------------------------------------------------------------#
#create the association table between venue and artist

class Show(db.Model):
    __tablename__ = "artist_shows"
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=func.now())
    art_show = db.relationship("Artist", backref=db.backref("artist_show"))
    show_venue = db.relationship("Venue", backref=db.backref("show_venue"))

#rationale is venue and genre is many to many so for tables to be in 3NF, there must be an associate table
artist_genre_association = db.Table('artist_genre', db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True), db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))

#Genre and venue will have an associate table
venue_genre_association = db.Table('venue_genre', db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True), db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    talent = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(120), default="not looking for talent")
    genres = db.relationship('Genre', secondary=venue_genre_association, backref=db.backref('venue', lazy=True))
    #ven_artists = db.relationship("Artist", secondary="artist_shows")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE
    
    def __repr__(self):
        return f'Venue: {self.id} Name: {self.name}'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    venue_seek = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(120), default="not looking for venue")
    #venues = db.relationship('Venue', secondary=show, backref=db.backref('artists', lazy=True))
    genres = db.relationship('Genre', secondary=artist_genre_association, backref=db.backref('artists', lazy=True))
    #art_show = db.relationship("Venue", secondary="artist_shows")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

    def __repr__(self):
        return f'Artist_id: {self.id} Artist_Name: {self.name}'
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#create the associate table for genre and venue


class Genre(db.Model):
  __tablename__ = 'genre'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))

  def __repr__(self):
    return f'Genre_id: {self.id} Genre_name: {self.name}'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  today = datetime.datetime.now()
  try:
    all_venues = Venue.query.order_by(Venue.state).order_by(Venue.city).all()
    for venue in all_venues:
      venues = []
      city = venue.city
      state = venue.state
      all_areas = Venue.query.filter_by(city=city, state=state).all()
      for area in all_areas:
        shows = db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time > today).all()
        shows_count = 0
        if len(shows) > 0:
          shows_count = db.session.query(func.count(shows.start_time)).first()
          shows_count = len(shows_count)
        venues.append({"id": area.id, "name": area.name, "num_upcoming_shows": shows_count})
      data.append({"city":city, "state": state, "venues": venues})
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("There was an error")
  finally:
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data_searched = request.form.get("search_term", "")
  response = {"count": 0, "data": [], "num_upcoming_shows":0} #incase search results gets nothing have defaults
  found_venues = Venue.query.filter(Venue.name.ilike(f'%{data_searched}%'))
  response["count"] = found_venues.count()
  today = datetime.datetime.now()

  for venue in found_venues:
    num_coming_shows = db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time > today).count()
    ind_artist = {"id":venue.id,"name":venue.name, "num_upcoming_shows":num_coming_shows}
    response["data"].append(ind_artist)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  today = datetime.datetime.now()
  try:
    requested_venue = Venue.query.get(venue_id)
    genres = []
    for genre in requested_venue.genres: #loop through genres relationship
      genres.append(genre)
    past_shows = []
    all_shows_at_venue = Show.query.filter_by(venue_id = venue_id)
    only_past_shows = all_shows_at_venue.filter(Show.start_time < today)
    for show in only_past_shows: #loop through past shows adding one show at a time
      artist = Artist.query.get(show.artist_id)
      show_dict = {
        "artist_id" : artist.id,
        "artist_name" : artist.name,
        "artist_image_link" : artist.image_link,
        "start_time" : show.start_time
      }
      past_shows.append(show_dict)
    
    only_future_shows = all_shows_at_venue.filter(Show.start_time > today)
    future_shows = []
    for show in only_future_shows: #loop through future shows adding one show at a time
      artist = Artist.query.get(show.artist_id)
      show_dict = {
        "artist_id" : artist.id,
        "artist_name" : artist.name,
        "artist_image_link" : artist.image_link,
        "start_time" : show.start_time
      }
      future_shows.append(show_dict)
    data["upcoming_shows"] = future_shows
    data["past_shows"] = past_shows
    data["genres"] = genres
    data["id"] = requested_venue.id
    data["name"] = requested_venue.name
    data["address"] = requested_venue.address
    data["city"] = requested_venue.city
    data["state"] = requested_venue.state
    data["phone"] = requested_venue.phone
    data["website"] = requested_venue.website
    data["facebook_link"] = requested_venue.facebook_link
    data["seeking_talent"] = requested_venue.talent
    data["seeking_description"] = requested_venue.seeking_desc
    data["image_link"] = requested_venue.image_link
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(future_shows)
  except:
    print(sys.exc_info())
    flash("There was an error in gettting the requested venue")
  finally:
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get("name")
    state = request.form.get("state")
    city = request.form.get("city")
    address = request.form.get("address")
    phone = request.form.get("phone")
    facebook_link = request.form.get("facebook_link")
    website_link = request.form.get("website_link")
    image_link = request.form.get("image_link")
    seeking_talent = request.form.get("seeking_talent")
    seeking_description = request.form.get("seeking_description")
    genres = request.form.getlist("genres")
    id = 504
    talent = False
    if seeking_talent == 'y':
      talent = True
    this_venue = Venue(id = id, name = name, state = state, city = city, address = address, phone = phone, facebook_link = facebook_link, website = website_link, image_link = image_link, talent = talent, seeking_desc = seeking_description)
    #loop over each genre in the list and dertemine if the genre exists in Genre table
    #if it doesnt exist first add it to the genre table
    current_genres = []
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count() > 0:
        #this_venue.genres.extend([this_genre])
        current_genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        current_genres.append(this_genre)
    this_venue.genres.extend(current_genres)
    db.session.add(this_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue ' + request.form['name'] + ' could not be listed!')
  finally:
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_to_be_deleted = db.session.query(Venue).filter(Venue.id==venue_id).first()
    db.session.delete(venue_to_be_deleted)
    db.session.commit()
    flash(f"Venue with id {venue_id} was successfully deleted" )
  except:
    db.session.rollback()
    flash(f"Venue with id {venue_id} was not successfully deleted" )
  finally:
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  try:
    all_artists = Artist.query.order_by(Artist.name).all()
    artists = []
    for artist in all_artists:
      artist_dict = {"id": artist.id, "name": artist.name}
      artists.append(artist_dict)
  except:
    flash("Could not load artists")
  finally:
    return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    data_searched = request.form.get("search_term", "")
    response = {"count": 0, "data": [], "num_upcoming_shows":0} #incase search results gets nothing have defaults
    found_artist = Artist.query.filter(Artist.name.ilike(f'%{data_searched}%'))
    response["count"] = found_artist.count()
    today = datetime.datetime.now()

    for artist in found_artist:
      num_coming_shows = db.session.query(Show).filter(Show.artist_id==artist.id, Show.start_time > today).count()
      ind_artist = {"id":artist.id,"name":artist.name, "num_upcoming_shows":num_coming_shows}
      response["data"].append(ind_artist)
  except:
    flash("Something went wrong")
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = {}
  today = datetime.datetime.now()
  try:
    requested_artist = Artist.query.get(artist_id)
    genres = []
    for genre in requested_artist.genres: #loop through genres relationship
      genres.append(genre)
    past_shows = []
    all_shows_by_artist = Show.query.filter_by(artist_id = artist_id)
    only_past_shows = all_shows_by_artist.filter(Show.start_time < today)
    for show in only_past_shows: #loop through past shows adding one show at a time
      artist = Artist.query.get(show.artist_id)
      show_dict = {
        "artist_id" : artist.id,
        "artist_name" : artist.name,
        "artist_image_link" : artist.image_link,
        "start_time" : show.start_time
      }
      past_shows.append(show_dict)
    
    only_future_shows = all_shows_by_artist.filter(Show.start_time > today)
    future_shows = []
    for show in only_future_shows: #loop through future shows adding one show at a time
      artist = Artist.query.get(show.artist_id)
      show_dict = {
        "artist_id" : artist.id,
        "artist_name" : artist.name,
        "artist_image_link" : artist.image_link,
        "start_time" : show.start_time
      }
      future_shows.append(show_dict)
    data["upcoming_shows"] = future_shows
    data["past_shows"] = past_shows
    data["genres"] = genres
    data["id"] = requested_artist.id
    data["name"] = requested_artist.name
    data["address"] = requested_artist.address
    data["city"] = requested_artist.city
    data["state"] = requested_artist.state
    data["phone"] = requested_artist.phone
    data["website"] = requested_artist.website
    data["facebook_link"] = requested_artist.facebook_link
    data["seeking_venue"] = requested_artist.venue_seek
    data["seeking_description"] = requested_artist.seeking_desc
    data["image_link"] = requested_artist.image_link
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(future_shows)
  except:
    print(sys.exc_info())
    flash("There was an error in gettting the requested venue")
  finally:
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = {}
  try:
    artist = Artist.query.filter(Artist.id == artist_id)
    if artist.count()> 0:

      #form.id.data = artist.first().id
      form.name.data = artist.first().name
      form.city.data = artist.first().city
      form.state.data = artist.first().state
      form.phone.data = artist.first().phone
      form.genres.data = artist.first().genres
      form.facebook_link.data = artist.first().facebook_link
      form.image_link.data = artist.first().image_link
      form.website_link.data = artist.first().website
      form.seeking_venue.data = artist.first().venue_seek
      form.seeking_description.data = artist.first().seeking_desc
      artist = artist.first()
  except:
    flash("Something went wrong")
  finally:
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  venue_seek = False
  try:
    artist = Artist.query.get(artist_id)
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    #artist.address = request.form["address"]
    artist.phone = request.form["phone"]
    genres = request.form.getlist("genres")
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count()> 0:
        if this_genre.first().name not in artist.genres:
          artist.genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        artist.genres.append(this_genre)
    
    artist.facebook_link = request.form["facebook_link"]
    artist.image_link = request.form["image_link"]
    artist.website = request.form["website_link"]
    if request.form.get("seeking_venue") == 'y':
      venue_seek = True
    artist.venue_seek = venue_seek
    artist.seeking_desc = request.form["seeking_description"]
    artist.name = request.form["name"]
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f"Could not update the artist with id {artist_id}")
  finally:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = {}
  try:
    venue = Venue.query.filter(Venue.id == venue_id)
    if venue.count()> 0:
      #form.artist_id.data = venue.first().id
      form.name.data = venue.first().name
      form.city.data = venue.first().city
      form.address.data = venue.first().address
      form.state.data = venue.first().state
      form.phone.data = venue.first().phone
      form.genres.data = venue.first().genres
      form.facebook_link.data = venue.first().facebook_link
      form.image_link.data = venue.first().image_link
      form.website_link.data = venue.first().website
      form.seeking_talent.data = venue.first().talent
      form.seeking_description.data = venue.first().seeking_desc
      venue = venue.first()
  except:
    flash("Something went wrong")
    print(sys.exc_info())
  finally:
  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  talent = False
  try:
    venue = Venue.query.get(venue_id)
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.address = request.form["address"]
    venue.phone = request.form["phone"]
    genres = request.form.getlist("genres")
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count()> 0:
        if this_genre.first().name not in venue.genres:
          venue.genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        venue.genres.append(this_genre)
    
    venue.facebook_link = request.form["facebook_link"]
    venue.image_link = request.form["image_link"]
    venue.website = request.form["website_link"]
    if request.form.get("seeking_venue") == 'y':
      talent = True
    venue.talent = talent
    venue.seeking_desc = request.form["seeking_description"]
    venue.name = request.form["name"]
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f"Could not update the venue with id {venue_id}")
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form.get("name")
    state = request.form.get("state")
    city = request.form.get("city")
    #address = request.form.get("address")
    phone = request.form.get("phone")
    facebook_link = request.form.get("facebook_link")
    website_link = request.form.get("website_link")
    image_link = request.form.get("image_link")
    seeking_talent = request.form.get("seeking_talent")
    seeking_description = request.form.get("seeking_description")
    genres = request.form.getlist("genres")
    
    venue_seek = False
    if seeking_talent == 'y':
      venue_seek = True
    this_artist = Artist(id = 503,name = name, state = state, city = city, phone = phone, facebook_link = facebook_link, website = website_link, image_link = image_link, venue_seek = venue_seek, seeking_desc = seeking_description)
    #loop over each genre in the list and dertemine if the genre exists in Genre table
    #if it doesnt exist first add it to the genre table
    current_genres = []
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count() > 0:
        #this_artist.genres.extend([this_genre])
        current_genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        current_genres.append(this_genre)
    this_artist.genres.extend(current_genres)
    db.session.add(this_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Artist ' + request.form['name'] + ' could not be listed!')
  finally:
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  try:
    shows = Show.query.order_by(Show.venue_id).all()
    for show in shows:
      show_venue_name = Venue.query.filter_by(id=show.venue_id).first().name
      show_artist = Artist.query.filter_by(id=show.artist_id).first()
      show_details = {"venue_id": show.venue_id, "venue_name": show_venue_name, "artist_id": show.artist_id, "artist_name": show_artist.name, "artist_image_link": show_artist.image_link, "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')}
      data.append(show_details)

  except:
    flash("Could not process shows")
    print(sys.exc_info())
  finally:
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form["artist_id"]
    venue_id = request.form["venue_id"]
    start_time = request.form["start_time"]
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show was not succeesfully listed!')
  finally:
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

#for local testing only
def drop_create(app):
  app.drop_all()
  app.create_all()

def populate_artist():
  russell = Artist(name="Russell", city="Harare", state="NA", address="547 One way Harare", phone="547 335", image_link="http://images.com", facebook_link="facebook.com", website="www.me.com", venue_seek= False, seeking_desc="Not seeking talent")
  db.session.add(russell)
  db.session.commit()

def populate_venue():
  grand = Venue(name="Grand Hotel", city="Harare", state="CA", address="547 Another way Harare", phone="547 335", image_link="http://images.com", facebook_link="facebook.com", website="www.me.com", talent = False, seeking_desc="Not seeking venue")
  db.session.add(grand)
  db.session.commit()

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
