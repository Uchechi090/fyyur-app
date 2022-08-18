#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
    jsonify
)
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
# from config import DatabaseURI

from models import (
    Genre,
    venue_genres,
    artist_genres,
    Venue,
    Artist,
    Show
)
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# app.config.from_object(DatabaseURI)
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # num_upcoming_shows should be aggregated based on number of upcoming
    # shows per venue.

    data = []

    try:
        areas = db.session.query(
            Venue.city,
            Venue.state).distinct(
            Venue.city,
            Venue.state).all()

        for area in areas:
            list_of_venues = Venue.query.filter(
                Venue.state == area.state).filter(
                Venue.city == area.city).all()
            venue_arr = []

            for venue in list_of_venues:
                venue_obj = {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(
                        db.session.query(Show).filter_by(
                            venue_id=venue.id).filter(
                            Show.time_of_show > datetime.now()).all()),
                }
                venue_arr.append(venue_obj)

                data.append({
                    "city": area.city,
                    "state": area.state,
                    "venues": venue_arr
                })
        # print("data:", data)

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    response = {}

    try:
        search_term = request.form.get('search_term')
        search_results = db.session.query(Venue).filter(
            Venue.name.ilike("%{}%".format(search_term.replace(" ", "\\ ")))).all()

        result_data = []

        for result in search_results:
            venue_obj = {}
            venue_obj["id"] = result.id
            venue_obj["name"] = result.name
            venue_obj["num_upcoming_shows"] = len(result.shows)
            result_data.append(venue_obj)

        response["count"] = len(result_data)
        response["data"] = result_data

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    try:
        venue = Venue.query.get(venue_id)

        past_shows = []
        upcoming_shows = []
        genres = [genre.name for genre in venue.genres]

        for show in venue.shows:
            if show.time_of_show > datetime.now():
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.time_of_show))
                })
            if show.time_of_show < datetime.now():
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(str(show.time_of_show))
                })

        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm()
    error = False

    try:
        new_venue = Venue(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data,
            genres=[]
        )

        genres = form.genres.data
        for genre in genres:
            single_genre = Genre.query.filter_by(name=genre).one_or_none()
            new_venue.genres.append(single_genre)

        # db.session.add(new_venue)
        Venue.insert(new_venue)
        db.session.commit()

        db.session.refresh(new_venue)

        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return new_venue
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())

        # on successful db insert, flash success
        # flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash(
            'An error occurred. Venue ' +
            request.form['name'] +
            ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(new_venue)
    redirect(url_for('index'))


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    redirect(url_for('index'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    try:
        fields = ["id", "name"]
        data = db.session.query(Artist).options(load_only(*fields)).all()

        # db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    response = {}

    try:
        search_term = request.form.get('search_term')
        search_results = db.session.query(Artist).filter(
            Artist.name.ilike("%{}%".format(search_term.replace(" ", "\\ ")))).all()

        result_data = []

        for result in search_results:
            artist_obj = {}
            artist_obj["id"] = result.id
            artist_obj["name"] = result.name
            artist_obj["num_upcoming_shows"] = len(result.shows)
            result_data.append(artist_obj)

        response["count"] = len(result_data)
        response["data"] = result_data

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using
    # artist_id

    try:
        artist = Artist.query.get(artist_id)

        past_shows = []
        upcoming_shows = []
        genres = [genre.name for genre in artist.genres]

        for show in artist.shows:
            if show.time_of_show > datetime.now():
                upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.time_of_show))
                })
            if show.time_of_show < datetime.now():
                past_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.time_of_show))
                })

        data = {
            "id": artist_id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {}

    try:
        get_artist = Artist.query.get(artist_id)

        genres = [genre.name for genre in get_artist.genres]

        artist = {
            "id": get_artist.id,
            "name": get_artist.name,
            "genres": genres,
            "city": get_artist.city,
            "state": get_artist.state,
            "phone": get_artist.phone,
            "website": get_artist.website_link,
            "facebook_link": get_artist.facebook_link,
            "seeking_venue": get_artist.seeking_venue,
            "seeking_description": get_artist.seeking_description,
            "image_link": get_artist.image_link
        }

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm()

    try:
        get_artist = Artist.query.get(artist_id)

        get_artist.name = form.name.data,
        get_artist.city = form.city.data,
        get_artist.state = form.state.data,
        get_artist.phone = form.phone.data,
        get_artist.website = form.website_link.data,
        get_artist.facebook_link = form.facebook_link.data,
        get_artist.seeking_venue = form.seeking_venue.data,
        get_artist.seeking_description = form.seeking_description.data,
        get_artist.image_link = form.image_link.data,
        get_artist.genres = form.genres.data

        db.session.commit()

        db.session.refresh(get_artist)

        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())

        flash(
            'An error occurred. Artist ' +
            request.form['name'] +
            ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = {}

    try:
        get_venue = Venue.query.get(venue_id)

        genres = [genre.name for genre in get_venue.genres]

        venue = {
            "id": get_venue.id,
            "name": get_venue.name,
            "address": get_venue.address,
            "genres": genres,
            "city": get_venue.city,
            "state": get_venue.state,
            "phone": get_venue.phone,
            "website": get_venue.website_link,
            "facebook_link": get_venue.facebook_link,
            "seeking_talent": get_venue.seeking_talent,
            "seeking_description": get_venue.seeking_description,
            "image_link": get_venue.image_link
        }

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm()

    try:
        get_venue = Venue.query.get(venue_id)

        get_venue.name = form.name.data,
        get_venue.city = form.city.data,
        get_venue.state = form.state.data,
        get_venue.phone = form.phone.data,
        get_venue.address = form.address.data,
        get_venue.website = form.website_link.data,
        get_venue.facebook_link = form.facebook_link.data,
        get_venue.seeking_talent = form.seeking_talent.data,
        get_venue.seeking_description = form.seeking_description.data,
        get_venue.image_link = form.image_link.data,
        get_venue.genres = form.genres.data

        db.session.commit()

        db.session.refresh(get_venue)

        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())

        flash(
            'An error occurred. Venue ' +
            request.form['name'] +
            ' could not be updated.')
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
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm()
    error = False

    try:
        new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data,
            genres=[]
        )

        genres = form.genres.data
        for genre in genres:
            single_genre = Genre.query.filter_by(name=genre).one_or_none()
            new_artist.genres.append(single_genre)

        # db.session.add(new_artist)
        Artist.insert(new_artist)
        db.session.commit()

        db.session.refresh(new_artist)

        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return new_artist
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())

        # on successful db insert, flash success
        # flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
        # listed.')
        flash(
            'An error occurred. Artist ' +
            request.form['name'] +
            ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(new_artist)
    redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = []

    try:
        list_of_shows = db.session.query(Show).all()

        for show in list_of_shows:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.time_of_show))
            })

        db.session.commit()
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        redirect(url_for('index'))
    finally:
        db.session.close()
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
    error = False

    try:
        new_show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )

        # db.session.add(new_show)
        Show.insert(new_show)
        db.session.commit()

        db.session.refresh(new_show)

        flash('Show was successfully listed!')
        return new_show
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())

        # on successful db insert, flash success
        # flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(new_show)
    redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
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
