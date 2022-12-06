from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from dateutil.relativedelta import relativedelta

from . import db, login_required
from .models import Rider, Driver

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        login_type = request.form.get('loginType')

        if login_type == 'rider':
            user = Rider.query.filter_by(email=email).first()

            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    session['account_type'] = 'Rider'
                    login_user(user, remember=True)
                    return redirect(url_for('views.rider_dashboard'))
                else:
                    flash('Incorrect password.', category='error')
            else:
                flash('No rider exists with this email address!', category='error')
        elif login_type == 'driver':
            user = Driver.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    session['account_type'] = 'Driver'
                    return redirect(url_for('views.driver_dashboard'))
                else:
                    flash('Incorrect password.', category='error')
            else:
                flash('No Driver exists with this email address!', category='error')

    if 'account_type' in session:
        return render_template('login.html', user=current_user, role=session['account_type'])
    return render_template('login.html', user=current_user, role='None')


@auth.route('/logout')
@login_required(role="ANY")
def logout():
    logout_user()
    session['account_type'] = 'None'
    return redirect(url_for('auth.login'))


@auth.route('/rider-sign-up', methods=['GET', 'POST'])
def rider_sign_up():
    if request.method == 'POST':

        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        DOB = request.form.get('DOB')
        age_check = datetime.now() - relativedelta(years=16)
        age_string = age_check.strftime("%Y-%m-%d")

        # Input Validation Checks
        if Rider.query.filter_by(email=email).first():
            flash('A user with this email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(full_name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif DOB is None or DOB > age_string:
            flash('You must be 16 years old to ride.')
        else:
            new_user = Rider(email=email, name=full_name, password=generate_password_hash(password1), DOB=DOB,
                             number_of_trips=0)
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='success')
            return redirect(url_for('auth.login'))
    if 'account_type' in session:
        return render_template('rider_sign_up.html', user=current_user, role=session['account_type'])
    return render_template('rider_sign_up.html', user=current_user, role='None')


@auth.route('/driver-sign-up', methods=['GET', 'POST'])
def driver_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        criminal_check = request.form.get('driverCriminalCheck')
        DOB = request.form.get('DOB')
        age_check = datetime.now() - relativedelta(years=18)
        age_string = age_check.strftime("%Y-%m-%d")

        # Input Validation Checks
        if Driver.query.filter_by(email=email).first():
            flash('A user with this email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(full_name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif DOB is None or DOB > age_string or criminal_check is None:
            flash('Sorry, you do not meet the eligibility requirements to become a driver.', category='error')
        else:
            new_user = Driver(email=email, name=full_name, password=generate_password_hash(password1), DOB=DOB,
                              active=False, number_of_trips=0, rating=0)
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='success')
            return redirect(url_for('auth.login'))

    if 'account_type' in session:
        return render_template('driver_sign_up.html', user=current_user, role=session['account_type'])
    return render_template('driver_sign_up.html', user=current_user, role='None')
