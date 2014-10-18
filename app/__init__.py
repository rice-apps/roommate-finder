__author__ = 'fdrozdowski'

from flask import Flask
#import sqlalchemy
#import flask.ext.sqlalchemy

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

from app import views, models