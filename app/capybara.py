from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required)
from flask import (
    current_app,
    redirect,
    url_for,
    make_response,
    request,
    flash,
    abort,
    render_template,
    send_from_directory,
    Blueprint)
from datetime import datetime
import random

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


@capybara.route('/today')
def today():
    today = datetime.now().date()
    capy = db.session.query(Capybara)\
        .filter_by(date=today).first()
    if capy:
        return send_from_directory(
            app.config['CAPYBARA_PATH'],
            capy.filename
        )
    else:
        return abort(404)


@capybara.route('/capybaras/<path:filename>')
def files(filename):
    return send_from_directory(
        app.config['CAPYBARA_PATH'],
        filename
    )


@capybara.route('/vote/<string:category>')
def vote(category):
    today = datetime.now().date()
    capy = db.session.query(Capybara)\
        .filter_by(date=today).first()

    resp = make_response(redirect(url_for('.lol')))
    if capy:
        if category == 'cute':
            cute_cookie = request.cookies.get('cute_cookie')
            if cute_cookie != str(capy.id) or not cute_cookie:
                if capy.cute_votes:
                    capy.cute_votes += 1
                else:
                     capy.cute_votes = 1
                db.session.add(capy)
                db.session.commit()

                cute_cookie = str(capy.id)
                resp.set_cookie('cute_cookie', cute_cookie)
        elif category == 'funny':
            funny_cookie = request.cookies.get('funny_cookie')
            if funny_cookie != str(capy.id) or not funny_cookie:
                if capy.funny_votes:
                    capy.funny_votes += 1
                else:
                    capy.funny_votes = 1
                db.session.add(capy)
                db.session.commit()
                
                funny_cookie = str(capy.id)
                resp.set_cookie('funny_cookie', funny_cookie)

    return resp