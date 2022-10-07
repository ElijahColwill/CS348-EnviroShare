from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Input Validation Checks
        if len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            flash('Account Created!', category='success')

    return render_template('sign_up.html')


@auth.route('/driver-sign-up', methods=['GET', 'POST'])
def driver_sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        photo_name = request.form.get('driverPhoto')
        age_check = request.form.get('driverAgeCheck')
        criminal_check = request.form.get('driverCriminalCheck')

        # Input Validation Checks
        if len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 8 characters.', category='error')
        elif not photo_name:
            flash('You must include an Identification Photo to become a driver.', category='error')
        elif age_check is None or criminal_check is None:
            flash('Sorry, you do not meet the eligibility requirements to become a driver.', category='error')
        else:
            flash('Account Created!', category='success')

    return render_template('driver_sign_up.html')
