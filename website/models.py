from . import db
from flask_login import UserMixin


class Rider(db.Model, UserMixin):
    __tablename__ = 'Rider'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    DOB = db.Column(db.String(10))
    active = db.Column(db.Boolean)
    number_of_trips = db.Column(db.Integer)


class Driver(db.Model, UserMixin):
    __tablename__ = 'Driver'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    DOB = db.Column(db.String(10))
    active = db.Column(db.Boolean)
    number_of_trips = db.Column(db.Integer)
