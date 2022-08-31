# ----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
import sys
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate
from flask_moment import  Moment

#----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing link
    genres = db.Column(db.String(120))
    website = db.Column(db.String(150))
    seeking_talent = db.Column(db.Boolean, default= False, nullable=False)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show',  primaryjoin='Venue.id==Show.venue_id',\
      backref='venue', lazy=True, cascade= 'save-update')
    
    def __repr__(self):
          return f'<Venue ID: {self.id}, Name: {self.name}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    # genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # missing fields|
    website = db.Column(db.String(150))
    looking_for_venue = db.Column(db.Boolean, default= False, nullable=False)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show',primaryjoin='Artist.id==Show.artist_id',\
      cascade= 'save-update', backref='artist', lazy=True)
    
    def __repr__(self):
        return f'<Venue ID: {self.id}, Name: {self.name},  City: {self.name}, State: {self.name}>'

class Show(db.Model):
      __tablename__ = 'Show'
      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'),
        nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'),
        nullable=False)
      # start_time = db.Column(db.DateTime)
      start_time = db.Column(db.DateTime,  default=datetime.datetime.utcnow())
      
      
      def __repr__(self):
            return f'<Show ID: {self.id}, Artist_ID: {self.artist_id}, Venue_ID: {self.venue_id}>'
#----------------------------------------------------------------------------#