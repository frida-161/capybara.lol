from flask import (
    jsonify,
    Blueprint)
from flask_login import (
    current_user
)

from datetime import datetime

from app import db
from app.models import Capybara

api = Blueprint(
    'api', __name__)

@api.route('/stats')
def capys_left():
    today = datetime.now().date()
    capy_queue = db.session.query(Capybara)\
        .filter(Capybara.date >= today)\
        .order_by(Capybara.date).all()
    total_capys = db.session.query(Capybara)\
        .filter(Capybara.date < today)\
        .order_by(Capybara.date).all()
    first = total_capys[0].date
    since_first = today - first
    stats = {
        'capybaras_enqueued' : len(capy_queue),
        'total_capybaras' : len(total_capys),
        'first_capybara' : first.isoformat(),
        'capybaras_per_day' : len(total_capys) / since_first.days
    }
    return jsonify(stats)