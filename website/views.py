from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from . import login_required

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html', user=current_user)


@views.route('/rider-dashboard')
@login_required(role='rider')
def rider_dashboard():
    return render_template('rider_dashboard.html', user=current_user)


@views.route('/driver-dashboard')
@login_required(role='driver')
def driver_dashboard():
    return render_template('driver_dashboard.html', user=current_user)
