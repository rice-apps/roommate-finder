from flask import Flask
import flask.ext.sqlalchemy
from flask_cas import CAS


app = Flask(__name__)
app.config.from_object('config')

db = flask.ext.sqlalchemy.SQLAlchemy(app)
CAS(app)

from app import views, models
