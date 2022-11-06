from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user, logout_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from . import login_required, db
from .models import RiderPaymentInformation, DriverPaymentInformation, Rider, Driver, Car, CarType

settings = Blueprint('settings', __name__)


def delete_profile():
    if session['account_type'] == 'Rider':
        db.session.execute(text('''
                                DELETE FROM Rider
                                WHERE id = :id;
                                '''),
                           params={
                               'id': current_user.id
                           })
    else:
        db.session.execute(text('''
                                DELETE FROM Driver
                                WHERE id = :id;
                                '''),
                           params={
                               'id': current_user.id
                           })

    db.session.commit()


def delete_payment():
    if session['account_type'] == 'Rider':
        db.session.execute(text('''
                            DELETE FROM RiderPaymentInformation
                            WHERE rider_id = :id;
                            '''),
                           params={
                               'id': current_user.id
                           })
    else:
        db.session.execute(text('''
                            DELETE FROM DriverPaymentInformation
                            WHERE driver_id = :id;
                            '''),
                           params={
                               'id': current_user.id
                           })
    db.session.commit()


def delete_car():
    if session['account_type'] == 'Driver':
        db.session.execute(text('''
                        DELETE FROM Car
                        WHERE driver_id = :id;
                        '''),
                           params={
                               'id': current_user.id
                           })
        db.session.commit()


@settings.route('/settings', methods=['GET', 'POST'])
@login_required(role="ANY")
def settings_home():
    if request.method == 'POST':
        delete = request.form.get('delete')
        if delete == 'profile_delete':
            delete_payment()
            delete_car()
            delete_profile()

            logout_user()
            session['account_type'] = 'None'
            flash('Account Deleted!', category='success')
            return redirect(url_for('auth.logout'))
        elif delete == 'payment_delete':
            delete_payment()
            flash('Payment Information Deleted!', category='success')
        elif delete == 'car_delete':
            delete_car()
            flash('Car Information Deleted!', category='success')

    has_payment = False
    has_car = False

    payment_info = None
    car_info = None
    car_type_info = None

    if session['account_type'] == 'Rider':
        payment_info = RiderPaymentInformation.query.get(int(current_user.id))
    else:
        payment_info = DriverPaymentInformation.query.get(int(current_user.id))
        car_info = Car.query.filter_by(driver_id=current_user.id).first()
        if car_info:
            has_car = True
            car_type_info = CarType.query.filter_by(make=car_info.make, model=car_info.model,
                                                    year=int(car_info.year)).first()

    if payment_info:
        has_payment = True

    return render_template('settings/settings.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment,
                           has_car=has_car,
                           payment_info=payment_info,
                           car_info=car_info,
                           car_type_info=car_type_info)


@settings.route('/payment', methods=['GET', 'POST'])
@login_required(role="ANY")
def payment():
    if request.method == 'POST':
        if session['account_type'] == 'Rider':
            card_type = request.form.get('card_type')
            card_number = request.form.get('card_number')
            security_code = request.form.get('security_code')
            exp_date = request.form.get('exp_date')

            if not card_type or not exp_date:
                flash('Please fill out all fields to update information.', category='error')
            elif len(card_number) != 16 or not card_number.isnumeric():
                flash('Card number must be 16 digits.', category='error')
            elif len(security_code) != 3 or not security_code.isnumeric():
                flash('Security code must be 3 digits.', category='error')
            else:
                payment_info = RiderPaymentInformation.query.get(int(current_user.id))
                if not payment_info:
                    new_payment = RiderPaymentInformation(rider_id=current_user.id, card_type=card_type,
                                                          card_number=int(card_number),
                                                          security_code=int(security_code),
                                                          expiration_date=exp_date)
                    db.session.add(new_payment)
                    db.session.commit()
                else:
                    payment_info.card_type = card_type
                    payment_info.card_number = card_number
                    payment_info.security_code = security_code
                    payment_info.expiration_date = exp_date
                    db.session.commit()

                flash('Payment Information Updated!', category='success')
                return redirect(url_for('settings.settings_home'))
        else:
            account_number = request.form.get('account_number')
            routing_number = request.form.get('routing_number')
            holder_name = request.form.get('holder_name')
            institution_name = request.form.get('institution_name')

            if not holder_name or not institution_name:
                flash('Please fill out all fields to update information.', category='error')
            elif len(routing_number) != 9 or not routing_number.isnumeric():
                flash('Routing number must be 16 digits.', category='error')
            elif len(account_number) < 12 or len(account_number) > 17 or not account_number.isnumeric():
                flash('Account number must be between 12 and 17 digits.', category='error')
            else:

                payment_info = DriverPaymentInformation.query.get(int(current_user.id))
                if not payment_info:
                    new_payment = DriverPaymentInformation(driver_id=current_user.id,
                                                           account_number=int(account_number),
                                                           routing_number=int(routing_number),
                                                           account_holder_name=holder_name,
                                                           institution_name=institution_name)
                    db.session.add(new_payment)
                    db.session.commit()
                else:
                    payment_info.account_number = account_number
                    payment_info.routing_number = routing_number
                    payment_info.account_holder_name = holder_name
                    payment_info.institution_name = institution_name
                    db.session.commit()

                flash('Payment Information Updated!', category='success')
                return redirect(url_for('settings.settings_home'))

    return render_template('settings/payment.html',
                           user=current_user,
                           role=session['account_type'])


@settings.route('/profile', methods=['GET', 'POST'])
@login_required(role="ANY")
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if session['account_type'] == 'Rider':
            rider = Rider.query.get(current_user.id)
            if Rider.query.filter_by(email=email).first():
                flash('A user with this email already exists.', category='error')
            elif email and len(email) < 4:
                flash('Email must be at least 4 characters.', category='error')
            elif full_name and len(full_name) < 2:
                flash('Name must be greater than 1 character.', category='error')
            elif password1 and password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif password1 and len(password1) < 8:
                flash('Password must be at least 8 characters.', category='error')
            else:
                if email:
                    rider.email = email

                if full_name:
                    rider.name = full_name

                if password1:
                    rider.password = generate_password_hash(password1)

                db.session.commit()
                flash('Account Updated!', category='success')
                return redirect(url_for('settings.settings_home'))
        else:
            driver = Driver.query.get(current_user.id)
            if Driver.query.filter_by(email=email).first():
                flash('A user with this email already exists.', category='error')
            elif email and len(email) < 4:
                flash('Email must be at least 4 characters.', category='error')
            elif full_name and len(full_name) < 2:
                flash('Name must be greater than 1 character.', category='error')
            elif password1 and password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif password1 and len(password1) < 8:
                flash('Password must be at least 8 characters.', category='error')
            else:
                if email:
                    driver.email = email

                if full_name:
                    driver.name = full_name

                if password1:
                    driver.password = generate_password_hash(password1)

                db.session.commit()
                flash('Account Updated!', category='success')
                return redirect(url_for('settings.settings_home'))

    return render_template('settings/profile.html',
                           user=current_user,
                           role=session['account_type'])


@settings.route('/car', methods=['GET', 'POST'])
@login_required(role="Driver")
def car():
    if request.method == 'POST':
        license_plate = request.form.get('license_plate')
        state = request.form.get('state')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        color = request.form.get('color')
        octane = request.form.get('octane')
        mpg = request.form.get('mpg')

        if mpg == 0:
            carbon_per_mile = 100
        else:
            carbon_per_mile = 8887 / int(mpg)

        override = request.form.get('car_override')

        if len(license_plate) < 6:
            flash('License Plate must be at least six characters.', category='error')
        elif not state:
            flash('Please select a state.', category='error')
        elif len(make) < 3:
            flash('Make must be at least three characters.', category='error')
        elif len(model) < 3:
            flash('Model must be at least three characters.', category='error')
        elif not year or not year.isnumeric() or int(year) < 1000 or int(year) > 9999:
            flash('Please enter a four digit year.', category='error')
        elif len(color) < 3:
            flash('Color must be at least three characters.', category='error')
        elif not octane or not octane.isnumeric():
            flash('Please select a number for fuel octane. If your care is electric, enter 0.', category='error')
        elif not mpg or not mpg.isnumeric() or int(mpg) > 200:
            flash('Please enter a valid value for MPG. If your car is electric, enter 0.')
        else:
            car_type = db.session.execute(
                text('''
                    SELECT *
                    FROM CarType
                    WHERE model = :model AND make = :make AND year = :year;
                    '''),
                params={
                    'model': model,
                    'make': make,
                    'year': int(year)
                }
            ).first()

            if car_type:
                if car_type.fuel_octane != octane or car_type.mpg != mpg:
                    if override == 'yes':
                        db.session.execute(
                            text('''
                                UPDATE CarType
                                SET fuel_octane = :octane, mpg = :mpg, carbon_per_mile = :carbon_per_mile
                                WHERE model = :model AND make = :make AND year = :year;
                            '''),
                            params={
                                'model': model,
                                'make': make,
                                'year': int(year),
                                'octane': octane,
                                'mpg': mpg,
                                'carbon_per_mile': carbon_per_mile
                            }
                        )
                    else:
                        octane = car_type.fuel_octane
                        mpg = car_type.MPG
                        if mpg == 0:
                            carbon_per_mile = 100
                        else:
                            carbon_per_mile = 8887 / int(mpg)
            else:
                db.session.execute(
                    text('''
                        INSERT INTO CarType(make, model, year, fuel_octane, MPG, carbon_per_mile)
                        VALUES(:make, :model, :year, :octane, :mpg, :carbon_per_mile);
                        '''),
                    params={
                        'model': model,
                        'make': make,
                        'year': int(year),
                        'octane': octane,
                        'mpg': mpg,
                        'carbon_per_mile': carbon_per_mile
                    }
                )
            db.session.execute(
                text('''
                    INSERT INTO Car(license_plate, state, driver_id, make, model, year, color)
                    VALUES(:license_plate, :state, :driver_id, :make, :model, :year, :color);
                    '''),
                params={
                    'license_plate': license_plate,
                    'state': state,
                    'driver_id': current_user.id,
                    'make': make,
                    'model': model,
                    'year': int(year),
                    'color': color
                }
            )
            db.session.commit()
            return redirect(url_for('settings.settings_home'))

    car_query = Car.query.filter_by(driver_id=current_user.id).first()
    if car_query:
        flash('Please delete your current car before adding a new one!', category='error')
        return redirect(url_for('settings.settings_home'))

    return render_template('settings/car.html',
                           user=current_user,
                           role=session['account_type'])
