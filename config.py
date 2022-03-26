import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
DB_HOST = os.environ.get('DB_HOST','127.0.0.1:5432')
DB_NAME = os.environ.get('DB_NAME','fyyurdb')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'pass123')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pass123@localhost:5432/fyyurdb'
SQLALCHEMY_DATABASE_URI = DB_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False