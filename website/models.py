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


class RiderPaymentInformation(db.Model):
    __tablename__ = 'RiderPaymentInformation'
    __table_args__ = {'extend_existing': True}

    rider_id = db.Column(db.Integer, db.ForeignKey('Rider.id'), primary_key=True)
    card_type = db.Column(db.String(150))
    card_number = db.Column(db.BigInteger)
    expiration_date = db.Column(db.String(150))
    security_code = db.Column(db.Integer)


class DriverPaymentInformation(db.Model):
    __tablename__ = 'DriverPaymentInformation'
    __table_args__ = {'extend_existing': True}
    
    driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'), primary_key=True)
    account_number = db.Column(db.BigInteger)
    routing_number = db.Column(db.BigInteger)
    account_holder_name = db.Column(db.String(150))
    institution_name = db.Column(db.String(150))
