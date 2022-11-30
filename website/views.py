from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import current_user

from datetime import datetime
from . import login_required
from .models import RiderPaymentInformation, DriverPaymentInformation, Car

views = Blueprint('views', __name__)


@views.route('/')
def home():
    try:
        if session['account_type']:
            if session['account_type'] == 'Rider':
                return redirect(url_for('views.rider_dashboard'))
            elif session['account_type'] == 'Driver':
                return redirect(url_for('views.driver_dashboard'))
        return render_template('home.html', user=current_user)
    except:
        return render_template('home.html', user=current_user)


@views.route('/rider-dashboard')
@login_required(role="Rider")
def rider_dashboard():
    has_payment = False
    if RiderPaymentInformation.query.get(current_user.id):
        has_payment = True

    return render_template('rider_dashboard.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment)


@views.route('/driver-dashboard')
@login_required(role="Driver")
def driver_dashboard():
    has_payment = False
    has_car = False
    if DriverPaymentInformation.query.get(current_user.id):
        has_payment = True
    if Car.query.filter_by(driver_id=current_user.id).first():
        has_car = True
    return render_template('driver_dashboard.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment,
                           has_car=has_car)
