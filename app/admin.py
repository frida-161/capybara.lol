"""Admin end points."""
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
    abort,
    Blueprint)
from datetime import datetime, timedelta
from werkzeug.urls import url_parse
from sqlalchemy import desc
from pathlib import Path
import hashlib


from app.models import User, Capybara
from app.helpers import generate_filename, update_hashes
from app import login_manager, db, app

admin = Blueprint('admin', __name__, template_folder='templates/admin')

@login_manager.user_loader
def load_user(user_id):
    """Load a user by id."""
    return db.session.query(User).filter_by(id=user_id).first()


@admin.route('/login', methods=['GET', 'POST'])
def login():
    """Log in the user."""
    if current_user.is_authenticated:
        return redirect(url_for('.upload'))
    if request.method == 'POST':
        user = db.session.query(User)\
            .filter_by(name=request.form.get('username')).first()
        if user is None or \
                not user.check_password(request.form.get('password')):
            flash('Invalid username or password')
            return redirect(url_for('.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('.upload')
        return redirect(next_page)
    else:
        return render_template('login.html')


@admin.route('/logout')
def logout():
    """Log out the user."""
    logout_user()
    return redirect(url_for('capybara.lol'))


@admin.route('/users')
@login_required
def get_users():
    """List all users."""
    if not current_user.superuser:
        return abort(401)
    users = db.session.query(User).all()
    return render_template('users.html', users=users)


@admin.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add a new User to the Database."""
    if not current_user.superuser:
        return abort(401)
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        if name is None or password is None:
            flash("Enter Username and password")
            return redirect(url_for('.add_user'))
        existing_user = db.session.query(User).filter_by(name=name).first()
        if existing_user:
            flash("An user with that name already exists")
            return redirect(url_for('.add_user'))
        elif len(password) < 8:
            flash("password needs to have at least 8 characters")
            return redirect(url_for('.add_user'))
        else:
            if request.form.get('superuser'):
                superuser = True
            else:
                superuser = False
            user = User(
                name=name,
                superuser=superuser)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("successfuly created user: %s" % name)
            current_app.logger.info('USER_CREATED: %s(%s) by user %s'
                            % (user.name, user.id, current_user.name))
            return redirect(url_for('.get_users'))
    else:
        return render_template('user.html')


@admin.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit a given user."""
    if not current_user.superuser and\
        user_id != current_user.id:
        return abort(401)
    else:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return abort(404)
        if request.method == 'POST':
            changed = False
            password = request.form.get('password')
            if not (password is None or password == ''):
                if len(password) < 8:
                    flash("password needs to have at least 8 characters")
                    return redirect(url_for('edit_user', user_id=user_id))
                user.set_password(password)
                changed = True
                current_app.logger.info(
                    'USER_PASSWORD_CHANGED: changed password for %s by %s'
                    % (user.name, current_user.name))
            if request.form.get('superuser') \
                and not user.superuser \
                and user_id != current_user.id:
                user.superuser = True
                changed = True
                current_app.logger.info(
                    'USER_SUPERUSER_CHANGED: %s promoted to superuser by %s'
                    % (user.name, current_user.name))
            if user.superuser and request.form.get('superuser') is None \
                    and user.id != current_user.id:
                user.superuser = False
                changed = True
                current_app.logger.info(
                    'USER_SUPERUSER_CHANGED: %s demoted to user by %s'
                    % (user.name, current_user.name))
            if changed:
                db.session.add(user)
                db.session.commit()
                flash("successfuly changed user: %s" % user.name)
                if current_user.superuser:
                    return redirect(url_for('.get_users'))
                else:
                    return redirect(url_for('.queue'))
            else:
                flash("nothing changed")
                return redirect(url_for('.edit_user', user_id=user_id))
        else:
            return render_template('user.html', user=user)


@admin.route('/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    """Delete a given user."""
    if not current_user.superuser:
        return abort(401)
    elif user_id == current_user.id:
        flash("can't delete yourself")
        return redirect(url_for('.get_users'))
    else:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return abort(404)
        capybaras = db.session.query(Capybara).filter_by(user_id=user.id).all()
        for c in capybaras:
            c.user_id = current_user.id
        db.session.add_all(capybaras)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        flash("removed user %s" % user.name)
        current_app.logger.info('USER_REMOVED: %s(%s) by user %s'
                        % (user.name, user.id, current_user.name))
        return redirect(url_for('.get_users'))


@admin.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('no file part')
            return redirect(url_for('.upload'))
        
        file = request.files['file']

        if file.filename == '':
            flash('no file selected')
            return redirect(url_for('.upload'))

        if not file.filename.endswith('.png') and\
            not file.filename.endswith('.jpg') and\
            not file.filename.endswith('.gif') and\
            not file.filename.endswith('.jpeg'):
            flash('wrong filetype')
            return redirect(url_for('.upload'))

        capy_path = Path(app.config['CAPYBARA_PATH'])
        file_content = file.read()
        hash  = hashlib.md5(file_content).hexdigest() 
        hash_path = capy_path / 'hashes.md5'

        # check for duplicates
        with open(hash_path, 'r') as hash_file:
            hashes = [h.strip() for h in hash_file.readlines()]
            app.logger.info(hash)
            app.logger.info(hashes)
            if hash in hashes:
                flash('this ain\'t copybara.lol')
                return redirect(url_for('.upload'))

        # save capybara
        filename = generate_filename(file.filename)
        file_path = capy_path / Path(filename)
        with open(file_path, 'wb') as out_file:
            out_file.write(file_content)

        # append hash
        with open(hash_path, 'a') as hash_file:
            hash_file.write('\n{}'.format(hash))

        today = datetime.now().date()

        date = db.session.query(Capybara.date)\
            .filter(Capybara.date >= today)\
            .order_by(desc(Capybara.date)).first()

        if date:
            new_date = date[0] + timedelta(days=1)
        else:
            new_date = today

        capy = Capybara(
            date=new_date,
            filename=filename,
            user_id=current_user.id
        )
        db.session.add(capy)
        db.session.commit()
        flash('capybara upgeloaded ;)')
        return redirect(url_for('.upload'))
    else:
        return render_template('upload.html')
    

@admin.route('/capy/<int:capy_id>/delete')
@login_required
def delete_capy(capy_id):
    if not current_user.superuser:
        abort(401)
    else:
        capy = db.session.query(Capybara).filter_by(id=capy_id).first()
        if capy:
            today = datetime.now().date()
            if capy.date < today:
                flash('can\'t delete old capys')
                return redirect(url_for('.queue'))
            later_capys = db.session.query(Capybara)\
                .filter(Capybara.date > capy.date)\
                .all()
            db.session.delete(capy)
            for c in later_capys:
                c.date = c.date - timedelta(days=1)
            db.session.commit()
            capy_path = Path(app.config['CAPYBARA_PATH']) / Path(capy.filename)
            capy_path.unlink()
            update_hashes()
        else:
            abort(404)
    return redirect(url_for('.queue'))


@admin.route('/')
@login_required
def queue():
    today = datetime.now().date()
    capy_queue = db.session.query(Capybara)\
        .filter(Capybara.date >= today)\
        .order_by(Capybara.date).all()
    return render_template('queue.html', queue=capy_queue)