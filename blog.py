from crypt import methods
from os import abort
from flask import (
    Blueprint,
    Flask,
    render_template,
    request,
    g,
    redirect,
    url_for,
    flash
)
from flask_app.auth import login_required
from flask_app.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created_at, author_id, username'
        ' FROM post p join user u on p.author_id = u.id'
        ' ORDER BY created_at DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Title is required!'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post(title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created_at, author_id'
        ' FROM post p JOIN user u on p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f'Post with ID:[{id}] does not exist')
    if check_author and g.user['id'] != post['author_id']:
        abort(403)
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Title is required!'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # using get_post so if logged in user is not the owner, it will raise error
    get_post(id)
    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?', (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))
