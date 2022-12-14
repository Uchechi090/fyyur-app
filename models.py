import datetime
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


venue_genres = db.Table(
    'venue_genres',
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id'),
        primary_key=True),
    db.Column(
        'venue_id',
        db.Integer,
        db.ForeignKey('Venue.id'),
        primary_key=True))

artist_genres = db.Table(
    'artist_genres',
    db.Column(
        'genre_id',
        db.Integer,
        db.ForeignKey('Genre.id'),
        primary_key=True),
    db.Column(
        'artist_id',
        db.Integer,
        db.ForeignKey('Artist.id'),
        primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship(
        'Genre',
        secondary='venue_genres',
        backref='venue',
        lazy=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, address: {self.address}>'

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship(
        'Genre',
        secondary='artist_genres',
        backref='artist',
        lazy=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, phone: {self.phone}>'

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    # image_link = db.Column(db.String(500))
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'),
        nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    time_of_show = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}, time: {self.time_of_show}, image: {self.image_link}>'

# TODO Implement Show and Artist models, and complete all model
# relationships and properties, as a database migration.
