#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from models import db, Venue, Show, Artist
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_sqlalchemy import SQLAlchemy
from forms import *
from flask_migrate import Migrate
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Regexp, URL, InputRequired, ValidationError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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

# db.create_all()

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
      data = []
      area_data = db.session.query(Venue).group_by(Venue.id, Venue.city, Venue.state).all()
      
      for area in area_data:
            venue_data = []
            city = area.city
            state = area.state
            venues = db.session.query(Venue).\
              filter_by(city=city, state=state).all()
              
            for venue in venues:
                  upcoming_shows=db.session.query(Show)\
                    .filter(Show.venue_id==venue.id, Show.start_time > datetime.datetime.now())\
                    .all()
                   
                  venue_data.append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': len(upcoming_shows)
                  })
            
            data.append({
              'city': city,
              'state': state,
              'venues': venue_data
              })
      return render_template('pages/venues.html', areas=data)
      


@app.route('/venues/search', methods=['POST'])
def search_venues():
  '''implement search on artists with partial string search''' 
  
  search_keyword = request.form.get('search_term', '')
  venue_list = db.session.query(Venue).all()


  search_list = []
  for venue in venue_list:
      
        if search_keyword.casefold() in venue.name.casefold():
          search_list.append({
            'id': venue.id,
            'name': venue.name,
          })
        print (search_list)
  response ={
    "count": len(search_list),
    "data": search_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter(Venue.id == venue_id).first()


  if data.genres is not None:
    data.genres = data.genres.split(",")
  
  past_shows = db.session.query(Show)\
    .filter(Show.venue_id == venue_id, Show.start_time < datetime.datetime.now())\
    .all()
 
  if len(past_shows) != 0:
        past_show_list = []
        
        for show in past_shows:
              artist = db.session.query(Artist)\
                .filter(Artist.id == show.artist_id)\
                .first()
              print(artist)
              
              past_show_list.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(show.start_time),
                
              })
              
        data.past_shows = past_show_list
        data.past_shows_count = len(past_show_list)
        
  
  upcoming_shows = db.session.query(Show)\
    .filter(Show.venue_id == venue_id, Show.start_time > datetime.datetime.now())\
    .all()
  
    
  if len(upcoming_shows) != 0:
        upcoming_show_list = []
        
        for show in upcoming_shows:
              artist = db.session.query(Artist)\
                .filter(Artist.id == show.artist_id)\
                .first()
              
              upcoming_show_list.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': str(show.start_time),
                
              })
        print(upcoming_show_list)
        data.upcoming_shows = upcoming_show_list
        data.upcoming_shows_count = len(upcoming_show_list)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertio
  
  form = VenueForm(request.form)
  if form.validate_on_submit():
        # new_venue = VenueForm()
        venue= Venue(name = form.name.data,
                 city = form.city.data,
                 state = form.state.data,
                 address = form.address.data,
                 phone = form.phone.data,
                 image_link = form.image_link.data,
                 facebook_link = form.facebook_link.data, 
                 genres = form.genres.data,
                 website = form.website_link.data,
                 seeking_talent = form.seeking_talent.data,
                 seeking_description = form.seeking_description.data,
                 )
        db.session.add(venue)
        db.session.commit()
        flash('Venue' + request.form['name'] + ' successfully created!')
  else:
        for field, message in form.errors.items():
              flash(field + ' - ' + str(message), 'danger')
        db.session.rollback()
        
  return render_template('forms/new_venue.html', form=form)

  # try:
  #   new_venue = VenueForm()
  #   venue= Venue(name = new_venue.name.data,
  #                city = new_venue.city.data,
  #                state = new_venue.state.data,
  #                address = new_venue.address.data,
  #                phone = new_venue.phone.data,
  #                image_link = new_venue.image_link.data,
  #                facebook_link = new_venue.facebook_link.data, 
  #                genres = new_venue.genres.data,
  #                website = new_venue.website_link.data,
  #                seeking_talent = new_venue.seeking_talent.data,
  #                seeking_description = new_venue.seeking_description.data,
  #                )
  #   db.session.add(venue)
  #   db.session.commit()
  #   flash('Venue' + request.form['name'] + ' successfully created!')
  # except:
  #   flash('An error occurred.' + request.form['name']  + request.form['name']+ ' was not created.')
  #   db.session.rollback()
  #   print(sys.exc_info())
  # finally:
  #   db.session.close()
    
  #   return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
      
      # form = VenueForm()
      error = False
      try:
        venue_to_delete = Venue.query.get_or_404(id=venue_id)
        db.session.delete(venue_to_delete)  
        db.session.commit()
        flash('Venue ' + venue_to_delete.name + ' deleted successfully!')
        
        return render_template('pages/home.html')
      except:
        db.session.rollback()
        flash('Whoops! there was a problem deleting the venue, try again')
        if error:
              abort(500)
              print(sys.exc_info())
        return render_template('pages/home.html')
      finally:
        db.session.close()
        
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
        # return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
      data = Artist.query.order_by('id').all()
      print(data)
  
      return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_keyword = request.form.get('search_term', '')
  artist_list = db.session.query(Artist).all()

  search_list = []
  for artist in artist_list:
        if search_keyword.casefold() in artist.name.casefold():
          search_list.append({
            'id': artist.id,
            'name': artist.name,
          })
        print (search_list)
        
        
  response ={
    "count": len(search_list),
    "data": search_list
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  data = Artist.query.filter(Artist.id == artist_id).first()
  print(data)
  
  if data.genres is not None:
    data.genres = data.genres.split(",")
  
  past_shows = db.session.query(Show)\
    .filter(Show.artist_id == artist_id, Show.start_time < datetime.datetime.now())\
    .all()
 
  if len(past_shows) != 0:
        past_show_list = []
        
        for show in past_shows:
              venue = db.session.query(Venue)\
                .filter(Venue.id == show.venue_id)\
                .first()
              print(venue)
              
              past_show_list.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(show.start_time),
                
              })
              
        data.past_shows = past_show_list
        data.past_shows_count = len(past_show_list)
        
  
  upcoming_shows = db.session.query(Show)\
    .filter(Show.artist_id == artist_id, Show.start_time > datetime.datetime.now())\
    .all()
  
    
  if len(upcoming_shows) != 0:
        upcoming_show_list = []
        
        for show in upcoming_shows:
              venue = db.session.query(Venue)\
                .filter(Venue.id == show.venue_id)\
                .first()
              
              upcoming_show_list.append({
                'venue_id': venue.id,
                'venue_name': venue.name,
                'venue_image_link': venue.image_link,
                'start_time': str(show.start_time),
                
              })
        print(upcoming_show_list)
        data.upcoming_shows = upcoming_show_list
        data.upcoming_shows_count = len(upcoming_show_list)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
      
  form = ArtistForm()
  # artist_data = db.session.query(Artist).filter(Artist.id == artist_id).first()
 
  
  artist = Artist.query.get_or_404(artist_id)
  # get all artist data update from form
  
  # form = ArtistForm(object=artist)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.looking_for_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
    
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
      try:
        artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
        
       
        artist.name = request.form.get('name')
        artist.genres = request.form.get('genres')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website_link')
        artist.facebook_link = request.form.get('name')
        artist.looking_for_venue = False if request.form.get('seeking_venue') is None else True

        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')
        
        db.session.commit()
        flash("Artist updated successfully! ")
      except:
        flash("Error," + request.form['name'] + " Artist update was unsuccessful!, please try again")
    
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()

      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.get_or_404(venue_id)
  form = VenueForm()
  
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data= venue.seeking_talent
  form.website_link.data= venue.website
  form.seeking_description.data = venue.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 
  try:
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
      
    venue.name = request.form.get('name')
    venue.genres = request.form.get('genres')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.website = request.form.get('website_link')
    venue.facebook_link = request.form.get('name')
    venue.seeking_talent = False if request.form.get('seeking_talent') is None else True

    venue.seeking_description = request.form.get('seeking_description')
    venue.image_link = request.form.get('image_link')
    
    db.session.commit()
    flash("venue updated successfully! ")
  except:
    flash("Error," + request.form['name'] + " venue update was unsuccessful!, please try again")

    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      # form = ArtistForm()
      try:
        artist = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        phone = request.form.get('phone'),
        image_link = request.form.get('image_link'),
        facebook_link = request.form.get('facebook_link'),
        genres = request.form.get('genres'),
        website = request.form.get('website'),
        looking_for_venue = False if request.form.get('seeking_venue') is None else True,
        seeking_description = request.form.get('seeking_description')
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist  ' + request.form['name'] + ' could not be listed.') 
        print(sys.exc_info())
      finally:
        db.session.close()
    
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      
  ''' displays list of shows at /shows'''
  
  show_list =  db.session.query(Show, Artist, Venue)\
    .select_from(Show).join(Artist)\
    .join(Venue).all()

  data= [{'venue_id': show.Venue.id,
          'venue_name': show.Venue.name,
          'artis_id': show.Artist.id,
          'artist_name': show.Artist.name,
          'artist_image_link': show.Artist.image_link,
          'start_time': str(show.Show.start_time),
    } for show in show_list]
  
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
  form = ShowForm()
  try:
    show = Show(
      venue_id = request.form.get('venue_id'),
      artist_id = request.form.get('artist_id'),
      start_time = request.form.get('start_time')
    )
  
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
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
