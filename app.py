#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from calendar import month
import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flaskapp import db, app
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flaskapp.forms import *
import datetime
import sys
from flaskapp.models import Show, Venue, Artist, Genre

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
        #shows = db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time > today)
        shows = db.session.query(Show).join(Venue, Show.venue_id==venue.id).filter(Show.start_time > today)
        shows_count = shows.count()
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
    #num_coming_shows = db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time > today).count()
    num_coming_shows = db.session.query(Show).join(Venue, Show.venue_id==venue.id).filter(Show.start_time > today).count()
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
        "start_time" : datetime.datetime.strftime(show.start_time,"%Y/%m/%d %H:%M")
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
    form = VenueForm(request.form)
    seeking_talent = form.seeking_talent.data
    talent = False
    if seeking_talent == 'y':
      talent = True
    venue = Venue(name=form.name.data,
    city=form.city.data, state=form.state.data,
    address=form.address.data, phone=form.phone.data,
     facebook_link=form.facebook_link.data,
    image_link=form.image_link.data,
    website_link=form.website_link.data,
    seeking_desc=form.seeking_description.data, talent=talent )
    #name = request.form.get("name")
    #state = request.form.get("state")
    #city = request.form.get("city")
    #address = request.form.get("address")
    #phone = request.form.get("phone")
    #facebook_link = request.form.get("facebook_link")
    #website_link = request.form.get("website_link")
    #image_link = request.form.get("image_link")
    #seeking_talent = request.form.get("seeking_talent")
    #seeking_description = request.form.get("seeking_description")
    #genres = request.form.getlist("genres")
    # this_venue = Venue(name = name, state = state, city = city, address = address, phone = phone, facebook_link = facebook_link, website = website_link, image_link = image_link, talent = talent, seeking_desc = seeking_description)
    #loop over each genre in the list and dertemine if the genre exists in Genre table
    #if it doesnt exist first add it to the genre table
    current_genres = []
    genres=form.genres.data
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count() > 0:
        current_genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        current_genres.append(this_genre)
    venue.genres.extend(current_genres)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
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
      #num_coming_shows = db.session.query(Show).filter(Show.artist_id==artist.id, Show.start_time > today).count()
      num_coming_shows = db.session.query(Show).join(Artist, Artist.id==Show.artist_id).filter(Show.start_time > today).count()
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
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.city = form.city.data
    artist.state = form.state.data
    #artist.address = request.form["address"]
    artist.phone = form.phone.data
    genres = form.genres.data
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count()> 0:
        if this_genre.first().name not in artist.genres:
          artist.genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        artist.genres.append(this_genre)
    
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    if form.seeking_venue.data == 'y':
      venue_seek = True
    artist.venue_seek = venue_seek
    artist.seeking_desc = form.seeking_description.data
    artist.name = form.name.data
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
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    genres = form.genres.data
    for genre in genres:
      this_genre = Genre.query.filter_by(name=genre)
      if this_genre.count()> 0:
        if this_genre.first().name not in venue.genres:
          venue.genres.append(this_genre.first())
      else:
        this_genre = Genre(name=genre)
        venue.genres.append(this_genre)
    
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    if form.seeking_venue.data == 'y':
      talent = True
    venue.talent = talent
    venue.seeking_desc = form.seeking_description.data
    venue.name = form.name.data
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
    form = ArtistForm(request.form)
    name = form.name.data
    state = form.state.data
    city = form.city.data
    #address = request.form.get("address")
    phone = form.phone.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    image_link = form.image_link.data
    seeking_venue = form.seeking_venue.data
    seeking_desc = form.seeking_description.data
    genres = form.genres.data
    
    venue_seek = False
    if seeking_venue == 'y':
      venue_seek = True
    this_artist = Artist(name = name, state = state, city = city, phone = phone, facebook_link = facebook_link, website = website, image_link = image_link, venue_seek = venue_seek, seeking_desc = seeking_desc)
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
    flash('Artist ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Artist ' + name + ' could not be listed!')
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
    form = ShowForm(request.form)
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
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

# #for local testing only
# def create():
#   populate_artist()
#   populate_venue()
#   populate_genres()
#   create_shows()

# def populate_artist():
#   import csv
#   artist_list = []
#   file_name = "to_de_deleted/artists.csv"
#   with open(file_name,"r") as file:
#     reader = csv.reader(file, delimiter=",")
#     #header = next(reader)
#     for row in reader:
#       artist = Artist(id=row[0], name=row[1], city=row[2], state=row[3], address=row[4], phone=[5], image_link=row[6], facebook_link=row[7], website=row[8], venue_seek=bool(row[9].title()), seeking_desc=row[10])
#       artist_list.append(artist)
#     db.session.add_all(artist_list)
#     db.session.commit()

# def populate_venue():
#   import csv
#   venue_list = []
#   file_name = "to_de_deleted/venues.csv"
#   with open(file_name,"r") as file:
#     reader = csv.reader(file, delimiter=",")
#     #header = next(reader)
#     for row in reader:
#       venue = Venue(id=row[0], name=row[1], city=row[2], state=row[3], address=row[4], phone=[5], image_link=row[6], facebook_link=row[7], website=row[8], talent=bool(row[9].title()), seeking_desc=row[10])
#       venue_list.append(venue)
#     db.session.add_all(venue_list)
#     db.session.commit()

# def populate_genres():
#   import csv
#   genre_list = []
#   file_name = "to_de_deleted/genres.csv"
#   with open(file_name,"r") as file:
#     reader = csv.reader(file, delimiter=",")
#     header = next(reader)
#     for row in reader:
#       genre = Genre(id=row[0], name=row[1])
#       genre_list.append(genre)
#     db.session.add_all(genre_list)
#     db.session.commit()

# def create_shows():
#   import csv
#   shows_list = []
#   file_name = "to_de_deleted/shows.csv"
#   with open(file_name,"r") as file:
#     reader = csv.reader(file, delimiter=",")
#     #header = next(reader)
#     for row in reader:
#       year = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").year
#       month = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").month
#       day = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").day
#       hr = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").hour
#       min = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").minute
#       sec = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M").second
#       new_date = datetime.datetime.strptime(row[2],"%d/%m/%Y %H:%M")
#       if year <= 2000:
#         new_date = datetime.datetime(2023, month, day, hr, min, sec)
#       show = Show(artist_id=row[0], venue_id=row[1], start_time=new_date)
#       shows_list.append(show)
#   db.session.add_all(shows_list)
#   db.session.commit()
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
