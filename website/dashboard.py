from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user, logout_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from . import login_required, db
from .models import RiderPaymentInformation, DriverPaymentInformation, Rider, Driver, Car, CarType

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/driver_dashboard')
@login_required(role="Driver")
def dashboard_home():
    has_payment = False
    has_car = False

    payment_info = None
    car_info = None
    car_type_info = None

    payment_info = DriverPaymentInformation.query.get(int(current_user.id))
    car_info = Car.query.filter_by(driver_id=current_user.id).first()
    if car_info:
        has_car = True
        car_type_info = CarType.query.filter_by(make=car_info.make, model=car_info.model,
                                                year=int(car_info.year)).first()

    if payment_info:
        has_payment = True

    return render_template('driver_dashboard.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment,
                           has_car=has_car,
                           payment_info=payment_info,
                           car_info=car_info,
                           car_type_info=car_type_info)
