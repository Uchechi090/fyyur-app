import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://uchechisamuel@localhost:5432/fyyurapp'

# class DatabaseURI:
#     DATABASE_NAME = "fyyurapp"
#     username = 'uchechisamuel'
#     url = 'localhost:5432'
#     SQLALCHEMY_DATABASE_URI = "postgres://{}@{}/{}".format(
#         username, url, DATABASE_NAME)
