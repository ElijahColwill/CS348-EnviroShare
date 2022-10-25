from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import current_user

from website import login_required

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html', user=current_user)


@views.route('/rider-dashboard')
@login_required(role="Rider")
def rider_dashboard():
    return render_template('rider_dashboard.html', user=current_user, role=session['account_type'])


@views.route('/driver-dashboard')
@login_required(role="Driver")
def driver_dashboard():
    return render_template('driver_dashboard.html', user=current_user, role=session['account_type'])
