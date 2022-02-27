from app.helpers import update_hashes
from app.models import User, Base, Capybara
from app import db

import sys

if __name__ == '__main__':
    if 'update_hashes' in sys.argv:
        update_hashes()
    
    if 'init_db' in sys.argv:
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