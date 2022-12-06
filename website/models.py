from sqlalchemy import ForeignKeyConstraint

from . import db
from flask_login import UserMixin
from datetime import datetime


class Rider(db.Model, UserMixin):
    __tablename__ = 'Rider'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    DOB = db.Column(db.String(10))
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
    rating = db.Column(db.Integer)


class RiderPaymentInformation(db.Model):
    __tablename__ = 'RiderPaymentInformation'
    __table_args__ = {'extend_existing': True}

    rider_id = db.Column(db.Integer, db.ForeignKey('Rider.id'), primary_key=True)
    card_type = db.Column(db.String(150))
    card_number = db.Column(db.BigInteger)
    expiration_date = db.Column(db.String(150))
    security_code = db.Column(db.Numeric(10, 2))


class DriverPaymentInformation(db.Model):
    __tablename__ = 'DriverPaymentInformation'
    __table_args__ = {'extend_existing': True}

    driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'), primary_key=True)
    account_number = db.Column(db.BigInteger)
    routing_number = db.Column(db.BigInteger)
    account_holder_name = db.Column(db.String(150))
    institution_name = db.Column(db.String(150))


class Car(db.Model):
    __tablename__ = 'Car'
    __table_args__ = (ForeignKeyConstraint(['make', 'model', 'year'],
                                           ['CarType.make', 'CarType.model', 'CarType.year'],
                                           name='CarTypeConstraint'),
                      {'extend_existing': True})

    license_plate = db.Column(db.String(12), primary_key=True)
    state = db.Column(db.String(30), primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'), primary_key=True)
    make = db.Column(db.String(150))
    model = db.Column(db.String(150))
    year = db.Column(db.Integer)
    color = db.Column(db.String(150))


class CarType(db.Model):
    __tablename__ = 'CarType'
    __table_args__ = {'extend_existing': True}

    make = db.Column(db.String(150), primary_key=True)
    model = db.Column(db.String(150), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    fuel_octane = db.Column(db.Numeric(10, 2))
    MPG = db.Column(db.Numeric(10, 2))
    carbon_per_mile = db.Column(db.Numeric(10, 2))


class EBikes(db.Model):
    __tablename__ = 'EBikes'
    __table_args__ = {'extend_existing': True}

    bike_id = db.Column(db.Integer, primary_key=True)
    current_station = db.Column(db.Integer, db.ForeignKey('Stations.station_id'))
    model = db.Column(db.String(150), db.ForeignKey('EBikeType.model'))


class EBikeType(db.Model):
    __tablename__ = 'EBikeType'
    __table_args__ = {'extend_existing': True}
    model = db.Column(db.String(150), primary_key=True)
    carbon_per_mile = db.Column(db.Numeric(10, 2))


class Stations(db.Model):
    __tablename__ = 'Stations'
    __table_args__ = {'extend_existing': True}

    station_id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(150))
    location = db.Column(db.String(150))
    distance_proxy = db.Column(db.Integer)


class Drives(db.Model):
    __tablename__ = 'Drives'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('Rider.id'), primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'), primary_key=True)
    start_datetime = db.Column(db.DateTime, primary_key=True)
    distance = db.Column(db.Numeric(10, 2))
    price = db.Column(db.Numeric(10, 2))
    carbon_cost = db.Column(db.Numeric(10, 2))


class Rents(db.Model):
    __tablename__ = 'Rents'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, db.ForeignKey('Rider.id'), primary_key=True)
    bike_id = db.Column(db.Integer, db.ForeignKey('EBikes.bike_id'), primary_key=True)
    start_datetime = db.Column(db.DateTime, primary_key=True)
    distance = db.Column(db.Numeric(10, 2))
    price = db.Column(db.Numeric(10, 2))
    carbon_cost = db.Column(db.Numeric(10, 2))
