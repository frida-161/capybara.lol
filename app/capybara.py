from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required)
from flask import (
    current_app,
    redirect,
    url_for,
    request,
    flash,
    render_template,
    send_from_directory,
    Blueprint)
from datetime import datetime

from app import db, app
from app.models import Capybara

capybara = Blueprint(
    'capybara', __name__, template_folder='templates/capybara')

@capybara.route('/')
def lol():
    today = datetime.now().date()
    capy = db.session.query(Capybara)\
        .filter_by(date=today).first()
    if capy:
        return render_template('capybara.html', capy=capy)
    else:
        return render_template('capybara.html')

@capybara.route('/capybaras/<path:filename>')
def files(filename):
    return send_from_directory(
        app.config['CAPYBARA_PATH'],
        filename
    )
