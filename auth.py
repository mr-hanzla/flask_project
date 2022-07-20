from crypt import methods
import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
# url_for: uses the name of the function, and not the @route name...
from werkzeug.security import check_password_hash, generate_password_hash
from flask_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def show(title, msg):
    print('-'*40)
    print(f'{title}: {msg}')
    print('-'*40)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        g.user = user
    else:
        g.user = None

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            password = 'Password is required'
        
        if error is None:
            try:
                db.execute(
                    'INSERT INTO user(username, password) values (?, ?)',
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f'User [{username}] already present!'
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        error = None
        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password!'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    # url_for takes in the name of the function.... not the route name!
    return redirect(url_for('blog.index'))
