from flaskapp import db
from sqlalchemy.sql import func
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

