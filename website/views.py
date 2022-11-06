from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user

from . import login_required, db
from .models import RiderPaymentInformation, DriverPaymentInformation, Rider, Driver

from werkzeug.security import generate_password_hash

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if session['account_type']:
        if session['account_type'] == 'Rider':
            return redirect(url_for('views.rider_dashboard'))
        else:
            return redirect(url_for('views.driver_dashboard'))
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
    if DriverPaymentInformation.query.get(current_user.id):
        has_payment = True
    return render_template('driver_dashboard.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment)


@views.route('/settings')
@login_required(role="ANY")
def settings():
    has_payment = False
    if session['account_type'] == 'Rider':
        payment_info = RiderPaymentInformation.query.get(int(current_user.id))
    else:
        payment_info = DriverPaymentInformation.query.get(int(current_user.id))

    if payment_info:
        has_payment = True

    return render_template('settings/settings.html', user=current_user,
                           role=session['account_type'],
                           has_payment=has_payment,
                           payment_info=payment_info)


@views.route('/payment', methods=['GET', 'POST'])
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
                                                          card_number=card_number,
                                                          security_code=security_code,
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
                return redirect(url_for('views.settings'))
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
                    new_payment = DriverPaymentInformation(driver_id=current_user.id, account_number=account_number,
                                                           routing_number=routing_number,
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
                return redirect(url_for('views.settings'))

    return render_template('settings/payment.html',
                           user=current_user,
                           role=session['account_type'])


@views.route('/profile', methods=['GET', 'POST'])
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
                return redirect(url_for('views.settings'))
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
                return redirect(url_for('views.settings'))

    return render_template('settings/profile.html',
                           user=current_user,
                           role=session['account_type'])


@views.route('/car')
@login_required(role="Driver")
def car():
    return render_template('settings/car.html',
                           user=current_user,
                           role=session['account_type'])
