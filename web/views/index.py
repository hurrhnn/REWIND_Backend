from flask import Blueprint, redirect, render_template, session, url_for, request, Response, flash

from flask_sqlalchemy import SQLAlchemy
from websocket.model import *

from db.initialize_db import db_session

from util import jwt_encode

callname = __name__.rsplit(".", 1)[-1]

bp = Blueprint(
    name=callname,
    import_name=__name__,
    url_prefix="/"
)


@bp.route('/')
def index():
    if 'logined' not in session:
        return redirect(url_for('index.login'))
    print(session['logined'])
    return render_template('index.html')


@bp.route('/login')
def login():
    return render_template('login.html')


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/logout')
def logout():
    # flash("Logout!!")
    session['logined'] = False
    return redirect(url_for('index.index'))
