from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user
from sqlalchemy import text

from datetime import datetime
from . import login_required, db
from .models import RiderPaymentInformation, DriverPaymentInformation, Car, Driver, Rider, EBikes, Stations

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


@views.route('/rider-dashboard-car', methods=['GET', 'POST'])
@login_required(role="Rider")
def rider_dashboard_car():
    if request.method == 'POST':
        loc = request.form.get('location')
        loc2 = request.form.get('location2')
        print(loc)
        print(loc2)
    return render_template('rider_dashboard_car.html', user=current_user,
                           role=session['account_type'])

@views.route('/rider-dashboard-bike', methods=['GET', 'POST'])
@login_required(role="Rider")
def rider_dashboard_bike():
    if request.method == 'POST':
        loc = request.form.get('location')
        station = Stations.query.all()
        print(station)
        print(loc)
    return render_template('rider_dashboard_bike.html', user=current_user,
                           role=session['account_type'])


@views.route('/driver-dashboard', methods=['GET', 'POST'])
@login_required(role="Driver")
def driver_dashboard():
    if request.method == 'POST':
        db.session.execute(text('''
                                    UPDATE Driver
                                    SET active = True
                                    WHERE id = :id;
                                            '''),
                           params={
                               'id': current_user.id
                           })
        db.session.commit()
        return render_template('driver_active.html', user=current_user,
                               role=session['account_type'])
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


@views.route('/driver-active', methods=['GET', 'POST'])
@login_required(role="Driver")
def driver_active():
    if request.method == 'POST':
        db.session.execute(text('''
                                        UPDATE Driver
                                        SET active = False
                                        WHERE id = :id;
                                        '''),
                           params={
                               'id': current_user.id
                           })
        db.session.commit()
        return render_template('driver_dashboard.html', user=current_user,
                               role=session['account_type'],
                               has_payment=True,
                               has_car=True)
    return render_template('driver_active.html', user=current_user,
                           role=session['account_type'])
