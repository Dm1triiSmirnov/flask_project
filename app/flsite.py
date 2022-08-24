import sqlite3
import os
from flask import (Flask, render_template, url_for,
                    request, flash, session,
                   redirect, abort, g)

from app.FDataBase import FDataBase


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'kal4jHCvj6#6sfs6df%6sdfssDf78Jjc'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

# menu = [{'name': 'Установка', 'url': 'install-flask'},
#         {'name': 'Первое приложение', 'url': 'first-app'},
#         {'name': 'Обратная связь', 'url': 'contact'}]


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route('/')
def index():
    return render_template('index.html',
                           menu=dbase.getMenu(),
                           posts=dbase.getPostsAnonce())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route('/post/<alias>')
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html',
                           menu=dbase.getMenu(),
                           title=title,
                           post=post)


if __name__ == '__main__':
    app.run(debug=True)
