from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from sqlalchemy import text

from . import login_required, db
from .models import Driver, Car, CarType

reports = Blueprint('reports', __name__)


@reports.route('/reports')
@login_required(role="ANY")
def reports_home():
    return render_template('reports/reports.html', user=current_user)


@reports.route('/search-drivers', methods=['GET', 'POST'])
@login_required(role="ANY")
def search_drivers():
    if request.method == 'POST':
        min_threshold = request.form.get('minimumRating')
        max_threshold = request.form.get('maximumRating')
        carbon_threshold = request.form.get('carbonThreshold')
        if not min_threshold or not max_threshold or not carbon_threshold:
            flash('Please select every field to perform a search.', category='error')
        else:
            drivers_rating_filter = db.session.execute(text('''
                                        SELECT * 
                                        FROM Driver
                                        WHERE rating >= :min AND rating <= :max;
                                    '''),
                                                       params={
                                                           'min': int(min_threshold),
                                                           'max': int(max_threshold)
                                                       }).all()
            drivers_rating_filter = Car.query.join(Driver, Driver.id == Car.driver_id) \
                .join(CarType, (CarType.make == Car.make) & (CarType.model == Car.model)
                      & (CarType.year == Car.year)) \
                .add_columns(Driver.id, Driver.name, Driver.number_of_trips, Driver.rating, Car.color, Car.make,
                             Car.model, Car.year) \
                .all()

            result_drivers = []
            for driver in drivers_rating_filter:
                matched_rides = db.session.execute(text('''
                                                        SELECT carbon_cost 
                                                        FROM Drives
                                                        WHERE driver_id = :id; 
                                                    '''),
                                                   params={
                                                       'id': driver.id
                                                   }).all()
                cost_sum = 0
                for ride in matched_rides:
                    cost_sum += ride.carbon_cost
                avg = cost_sum / len(matched_rides)
                if avg <= int(carbon_threshold):
                    result_drivers.append(driver)

            return render_template('reports/search_drivers_results.html', minimum_rating=min_threshold,
                                   maximum_rating=max_threshold,
                                   carbon_threshold=carbon_threshold, entries=result_drivers)

    return render_template('reports/search_drivers.html', user=current_user)

# @reports.route('/search-vehicles')
# @login_required(role="ANY")
# def search_vehicles():
#     return render_template('search_vehicles.html', user=current_user)
#
# @reports.route('/rider-leaderboard')
# @login_required(role="ANY")
# def rider_leaderboard():
#     return render_template('rider_leaderboard.html', user=current_user)
