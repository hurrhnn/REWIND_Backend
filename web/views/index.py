from flask import Blueprint, request, Response, redirect, render_template, session, url_for, json, flash

from flask_sqlalchemy import SQLAlchemy
from websocket.model import *

from db.database import db_session

from util import jwt_encode

callname = __name__.rsplit(".", 1)[-1]

bp = Blueprint(
    name=callname,
    import_name=__name__,
    url_prefix="/"
)


@bp.route('/')
def index():
    print(session['logined'])
    if not session['logined']:
        return redirect(url_for('index.login'))
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            email = request.form['email']
            pwd = request.form['password']
            data = User.query.filter_by(email=email, password=pwd).first()

            token = jwt_encode(json.loads(str(data)))

            obj = json.dumps({'type': 'authentication', 'payload': {'token': token}}, ensure_ascii=False).encode('utf8')

            if data is not None:
                session['logined'] = True
                return Response(response=obj, status=201, content_type='application/json')
            else:
                return Response(status=401)
        except Exception as e:
            print(e)
            return Response(status=401)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            new_user = User(name=name, email=email, password=password)

            if User.query.filter(User.email == email).first() is not None:
                flash('이메일이 이미 존재합니다')
                return render_template('register.html')

            db_session.add(new_user)
            db_session.commit()
            return redirect(url_for('index.login'))
        except Exception as e:
            print(e)
            return Response(status=401)
    return render_template('register.html')


@bp.route('/logout')
def logout():
    flash("Logout!!")
    session['logined'] = False
    return redirect(url_for('index.index'))
