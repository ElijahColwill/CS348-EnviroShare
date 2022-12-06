from functools import wraps

from flask import Flask, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = 'enviroshare'


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or 'account_type' not in session:
                return current_app.login_manager.unauthorized()
            if (session['account_type'] != role) and (role != "ANY"):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '348-demo'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqldb://Enviroshare:Enviroshare@127.0.0.1:3306/{DB_NAME}'
    db.init_app(app)

    from .models import Rider, Driver, Stations, EBikes, EBikeType

    from .views import views
    from .auth import auth
    from .settings import settings
    from .dashboard import dashboard

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(settings, url_prefix='/')
    app.register_blueprint(dashboard, url_prefix='/')

    with app.app_context():
        db.create_all()
        if len(Stations.query.all()) == 0:
            new_station = Stations(station_id=1, station_name="Purdue Memorial Union",
                                   location="PMU", distance_proxy=0)
            db.session.add(new_station)
            new_station = Stations(station_id=2, station_name="Stewart Center",
                                   location="STEW", distance_proxy=1)
            db.session.add(new_station)
            new_station = Stations(station_id=3, station_name="Lilly Hall",
                                   location="LILY", distance_proxy=2)
            db.session.add(new_station)
            new_station = Stations(station_id=4, station_name="Aspire Apartments",
                                   location="ASPIRE", distance_proxy=8)
            db.session.add(new_station)
            new_station = Stations(station_id=5, station_name="Horticulture Park",
                                   location="HORT", distance_proxy=12)
            db.session.add(new_station)
            new_station = Stations(station_id=6, station_name="Lafayette Courthouse",
                                   location="LAF", distance_proxy=18)
            db.session.add(new_station)
            new_station = Stations(station_id=7, station_name="Lafayette Zoo",
                                   location="ZOO", distance_proxy=20)
            db.session.add(new_station)
            new_station = Stations(station_id=8, station_name="Lafayette Ihop",
                                   location="IHOP", distance_proxy=22)
            db.session.add(new_station)
            new_station = Stations(station_id=9, station_name="Camp Cary",
                                   location="CARY", distance_proxy=30)
            db.session.add(new_station)
            new_station = Stations(station_id=10, station_name="Indianapolis",
                                   location="INDY", distance_proxy=125)
            db.session.add(new_station)
            db.session.commit()

        if len(EBikeType.query.all()) == 0:
            new_type = EBikeType(model="Tesla Model B", carbon_per_mile=2)
            db.session.add(new_type)
            new_type = EBikeType(model="Tesla Model I", carbon_per_mile=1)
            db.session.add(new_type)
            new_type = EBikeType(model="Tesla Model K", carbon_per_mile=5)
            db.session.add(new_type)
            new_type = EBikeType(model="Tesla Model E", carbon_per_mile=3)
            db.session.add(new_type)
            db.session.commit()

        if len(EBikes.query.all()) == 0:
            new_bike = EBikes(bike_id=1, current_station=1, model="Tesla Model B")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=2, current_station=1, model="Tesla Model I")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=3, current_station=3, model="Tesla Model I")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=4, current_station=4, model="Tesla Model I")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=5, current_station=5, model="Tesla Model K")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=6, current_station=6, model="Tesla Model K")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=7, current_station=7, model="Tesla Model E")
            db.session.add(new_bike)
            new_bike = EBikes(bike_id=8, current_station=8, model="Tesla Model E")
            db.session.add(new_bike)
            db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if 'account_type' in session:
            if session['account_type'] == 'Driver':
                return Driver.query.get(int(user_id))
            elif session['account_type'] == 'Rider':
                return Rider.query.get(int(user_id))
            else:
                return None
        return None

    return app
