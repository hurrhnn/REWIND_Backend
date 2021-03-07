from flask import Blueprint, request, render_template, Response, json, session, flash, redirect, url_for

from db.initialize_db import db_session
from util import jwt_encode
from websocket.model import User

callname = __name__.rsplit(".", 1)[-1]

bp = Blueprint(
    name=callname,
    import_name=__name__,
    url_prefix=f"/{callname}"
)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        email = request.form['email']
        pwd = request.form['password']
        data = User.query.filter_by(email=email, password=pwd).first()

        token = jwt_encode(json.loads(str(data)))

        obj = json.dumps({'type': 'authentication', 'payload': {'token': token}}, ensure_ascii=False).encode('utf8')

        if data is not None:
            return Response(response=obj, status=201, content_type='application/json')
        else:
            return Response(status=401)
    except Exception as e:
        print(e)
        return Response(status=401)


@bp.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)

        if User.query.filter(User.email == email).first() is not None:
            flash('이메일이 이미 존재합니다')
            return Response(status=400)

        db_session.add(new_user)
        db_session.commit()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=401)