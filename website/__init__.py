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

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Rider, Driver

    with app.app_context():
        db.create_all()

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
