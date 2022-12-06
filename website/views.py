from datetime import datetime
from decimal import Decimal
import json

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user
from sqlalchemy import text

from . import login_required, db
from .models import RiderPaymentInformation, DriverPaymentInformation, Car, Driver, Rider, EBikes, Stations, \
    EBikeType, CarType, Rents, Drives

views = Blueprint('views', __name__)

location_dict = {
    "PMU": "Purdue Memorial Union",
    "STEW": "Stewart Center",
    "LILY": "Lilly Hall",
    "ASPIRE": "Aspire Apartments",
    "HORT": "Horticulture Park",
    "LAF": "Lafayette Courthouse",
    "ZOO": "Lafayette Zoo",
    "IHOP": "Lafayette IHop",
    "CARY": "Camp Cary",
    "INDY": "Indianapolis"
}


@views.route('/')
def home():
    if not current_user.is_authenticated:
        session['account_type'] = None
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

        information_dict = request.form.get('rating_button')
        if information_dict:
            information_dict = eval(information_dict)
            rating = int(request.form.get('rating'))
            selected_driver = Driver.query.get(int(information_dict['id']))
            selected_driver.rating = (selected_driver.rating * (selected_driver.number_of_trips - 1) + rating) \
                                     / selected_driver.number_of_trips
            flash(f'Thank you for providing feedback!', category='success')
            new_ride = Drives(user_id=current_user.id, driver_id=int(information_dict['id']),
                              start_datetime=datetime.now(),
                              distance=float(information_dict['distance']),
                              price=float(information_dict['price']),
                              carbon_cost=float(information_dict['distance']) *
                                          float(information_dict['carbon_per_mile']))
            db.session.add(new_ride)
            db.session.commit()
            return redirect(url_for('views.rider_dashboard'))

        location_starting = request.form.get('location_starting')
        location_ending = request.form.get('location_ending')
        starting_station = Stations.query.filter_by(location=location_starting).first()
        ending_station = Stations.query.filter_by(location=location_ending).first()
        distance = Decimal(float(abs(starting_station.distance_proxy - ending_station.distance_proxy)))

        drive_ride = request.form.get('ride_button')

        if drive_ride:
            flash(f'Your ride was successful!', category='success')
            Rider.query.get(current_user.id).number_of_trips += 1
            Driver.query.get(int(drive_ride)).number_of_trips += 1
            db.session.commit()
            entry = Car.query.filter_by(driver_id=int(drive_ride)) \
                .join(CarType, (CarType.make == Car.make) & (CarType.model == Car.model)
                      & (CarType.year == Car.year)) \
                .add_columns(CarType.carbon_per_mile) \
                .first()
            return render_template('end_driving.html', driver_name=Driver.query.get(int(drive_ride)).name,
                                   information={"id": int(drive_ride),
                                                "distance": distance,
                                                "price": round(distance / 5 + (entry.carbon_per_mile *
                                                                               (distance / 500)), 2),
                                                "carbon_per_mile": entry.carbon_per_mile})
        elif location_starting:
            entries = Car.query.join(Driver, (Driver.id == Car.driver_id) & (Driver.active)) \
                .join(CarType, (CarType.make == Car.make) & (CarType.model == Car.model)
                      & (CarType.year == Car.year)) \
                .add_columns(Driver.id, Driver.name, Driver.email, Car.color, Car.make, Car.model,
                             Car.year, CarType.carbon_per_mile) \
                .all()
            return render_template('rider_dashboard_car.html', user=current_user,
                                   role=session['account_type'], start=starting_station, end=ending_station,
                                   entries=entries, distance=distance, location_dict=location_dict)

    return render_template('rider_dashboard_car.html', user=current_user,
                           role=session['account_type'], start=None, end=None,
                           entries=[], location_dict=location_dict)


@views.route('/rider-dashboard-bike', methods=['GET', 'POST'])
@login_required(role="Rider")
def rider_dashboard_bike():
    if request.method == 'POST':
        location_starting = request.form.get('location_starting')
        location_ending = request.form.get('location_ending')
        starting_station = Stations.query.filter_by(location=location_starting).first()
        ending_station = Stations.query.filter_by(location=location_ending).first()

        distance = Decimal(float(abs(starting_station.distance_proxy - ending_station.distance_proxy)))
        bike_rent = request.form.get('rent_button')

        if bike_rent:
            flash(f'Bike rented! Your ride is complete.', category='success')
            bike = EBikes.query.filter_by(bike_id=int(bike_rent)) \
                .join(EBikeType, EBikes.model == EBikeType.model) \
                .add_columns(EBikes.bike_id, EBikes.model, EBikeType.carbon_per_mile) \
                .first()
            new_rent = Rents(user_id=current_user.id, bike_id=int(bike_rent),
                             start_datetime=datetime.now(),
                             distance=distance,
                             price=round(distance / 7 + (bike.carbon_per_mile * (distance / 10)), 2),
                             carbon_cost=distance * bike.carbon_per_mile)
            db.session.add(new_rent)
            Rider.query.get(current_user.id).number_of_trips += 1
            EBikes.query.get(int(bike_rent)).current_station = int(ending_station.station_id)
            db.session.commit()
            return redirect(url_for('views.rider_dashboard'))
        elif location_starting:
            bikes = EBikes.query.filter_by(current_station=starting_station.station_id) \
                .join(EBikeType, EBikes.model == EBikeType.model) \
                .add_columns(EBikes.bike_id, EBikes.model, EBikeType.carbon_per_mile) \
                .all()
            return render_template('rider_dashboard_bike.html', user=current_user,
                                   role=session['account_type'], bikes_list=bikes,
                                   distance=distance, start=starting_station, end=ending_station,
                                   location_dict=location_dict)

    return render_template('rider_dashboard_bike.html', user=current_user,
                           role=session['account_type'], bikes_list=[], start=None,
                           end=None, location_dict=location_dict)


@views.route('/driver-dashboard', methods=['GET', 'POST'])
@login_required(role="Driver")
def driver_dashboard():
    if request.method == 'POST':
        status = request.form.get('active_button')
        if status:
            if status == 'start':
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
            else:
                db.session.execute(text('''
                                            UPDATE Driver
                                            SET active = False
                                            WHERE id = :id;
                                            '''),
                                   params={
                                       'id': current_user.id
                                   })
                db.session.commit()
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
