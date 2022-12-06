from flask import Blueprint, render_template, request, flash, session
from flask_login import current_user
from sqlalchemy import text

from . import login_required, db
from .models import Driver, Car, CarType

reports = Blueprint('reports', __name__)


@reports.route('/reports')
@login_required(role="ANY")
def reports_home():
    return render_template('reports/reports.html', user=current_user,
                           role=session['account_type'])


@reports.route('/search-vehicles', methods=['GET', 'POST'])
@login_required(role="ANY")
def search_vehicles():
    if request.method == 'POST':
        carbon_threshold = request.form.get('carbonThreshold')
        vehicle_type = request.form.get('vehicleType')
        if not vehicle_type or not carbon_threshold:
            flash('Please select every field to perform a search.', category='error')
        elif not carbon_threshold.isnumeric():
            flash('Please insert a number for the minimum carbon threshold', category='error')
        else:
            if vehicle_type == 'cars':
                cars_filtered = db.session.execute(text('''
                                                    SELECT CarType.make, CarType.model, CarType.year,
                                                        CarType.carbon_per_mile, COUNT(*) as number_of_rides
                                                    FROM Car
                                                    JOIN CarType
                                                    ON Car.model = CarType.model 
                                                    AND Car.make = CarType.make 
                                                    AND Car.year = CarType.year
                                                    JOIN Drives
                                                    ON Car.driver_id = Drives.driver_id
                                                    WHERE carbon_per_mile <= :max
                                                    GROUP BY CarType.make, CarType.model, CarType.year
                                                    ORDER BY number_of_rides DESC
                                                    LIMIT 10;
                                                '''),
                                                   params={
                                                       'max': int(carbon_threshold)
                                                   }).all()
                return render_template('reports/search_vehicles_results.html', carbon_threshold=int(carbon_threshold),
                                       vehicle_type=vehicle_type, entries=cars_filtered, user=current_user,
                                       role=session['account_type'])
            elif vehicle_type == 'ebikes':
                bikes_filtered = db.session.execute(text('''
                                                        SELECT EBikes.model, EBikeType.carbon_per_mile, 
                                                            COUNT(*) as number_of_rides
                                                        FROM EBikes
                                                        JOIN EBikeType
                                                        ON EBikes.model = EBikeType.model
                                                        JOIN Rents
                                                        ON EBikes.bike_id = Rents.bike_id
                                                        WHERE carbon_per_mile <= :max
                                                        GROUP BY EBikes.model
                                                        ORDER BY number_of_rides DESC
                                                        LIMIT 10;
                                                                '''),
                                                    params={
                                                        'max': int(carbon_threshold)
                                                    }).all()
                return render_template('reports/search_vehicles_results.html', carbon_threshold=int(carbon_threshold),
                                       vehicle_type=vehicle_type, entries=bikes_filtered, user=current_user,
                                       role=session['account_type'])

    return render_template('reports/search_vehicles.html')


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
            drivers_filtered = db.session.execute(text('''
                                        SELECT Driver.id, Driver.name, Driver.number_of_trips, Driver.rating,
                                            Car.make, Car.model, Car.year, Car.color,
                                            AVG(Drives.carbon_cost) as average_cost
                                        FROM Driver
                                        JOIN Drives
                                        ON Driver.id = Drives.driver_id
                                        JOIN Car
                                        ON Driver.id = Car.driver_id
                                        JOIN CarType
                                        ON Car.make = CarType.make
                                        AND Car.model = CarType.model
                                        AND Car.year = CarType.year
                                        WHERE rating >= :min AND rating <= :max
                                        GROUP BY Driver.id, Car.make, Car.model, Car.year, Car.color
                                        HAVING AVG(Drives.carbon_cost) <= :avg;
                                    '''),
                                                  params={
                                                      'min': int(min_threshold),
                                                      'max': int(max_threshold),
                                                      'avg': int(carbon_threshold)
                                                  }).all()

            return render_template('reports/search_drivers_results.html', minimum_rating=min_threshold,
                                   maximum_rating=max_threshold,
                                   carbon_threshold=carbon_threshold, entries=drivers_filtered,
                                   user=current_user,
                                   role=session['account_type'])

    return render_template('reports/search_drivers.html')
