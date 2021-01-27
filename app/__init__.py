"""A small Flask app to serve daily capybara."""
import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.models import User


app = Flask(__name__)

app.config.from_object('app.config')
if not os.path.exists(app.config['CAPYBARA_PATH']):
    os.makedirs(app.config['CAPYBARA_PATH'])

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin.login'

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


from app.admin import admin
app.register_blueprint(admin, url_prefix='/admin')
from app.capybara import capybara
app.register_blueprint(capybara, url_prefix='/')

from app.models import User, Capybara, Base
Base.metadata.create_all(db.engine)
users = db.session.query(User).all()
if len(users) == 0:
    su = User(
        name='admin',
        superuser=True
    )
    su.set_password('admin')
    db.session.add(su)
    db.session.commit()
