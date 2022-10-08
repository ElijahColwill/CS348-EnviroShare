from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_required
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        login_type = request.form.get('loginType')

        user = User.query.filter_by(email=email).first()

        if user:
            if user.role != login_type:
                flash('Incorrect Role, check if you are a rider or diver.', category='error')
            elif check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.role == 'rider':
                    return redirect(url_for('views.rider_dashboard'))
                else:
                    return redirect(url_for('views.driver_dashboard'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('No user exists with this email address!', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required(role='ANY')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':

        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Input Validation Checks
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(full_name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            new_user = User(role='rider', email=email, name=full_name, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='success')
            return redirect(url_for('views.rider_dashboard'))
    return render_template('sign_up.html', user=current_user)


@auth.route('/driver-sign-up', methods=['GET', 'POST'])
def driver_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        age_check = request.form.get('driverAgeCheck')
        criminal_check = request.form.get('driverCriminalCheck')

        # Input Validation Checks
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(full_name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif age_check is None or criminal_check is None:
            flash('Sorry, you do not meet the eligibility requirements to become a driver.', category='error')
        else:
            new_user = User(role='driver', email=email, name=full_name, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='success')
            return redirect(url_for('views.dashboard-driver'))

    return render_template('driver_sign_up.html', user=current_user)
