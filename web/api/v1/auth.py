import traceback
from hashlib import sha512

from flask import Blueprint
from flask import jsonify
from flask import request

from db.models import User
from util import jwt_encode, generate_snowflake
from web import db
from web.api.error import UnauthorizedException

bp = Blueprint(
    name="auth",
    import_name="auth",
    url_prefix="/auth"
)


@bp.post('/login')
def login():
    try:
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email is None or password is None:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "email or password is no provided."
                }
            }), 400

        password = sha512(password.encode('utf-8')).hexdigest()

        data = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if data is None:
            raise UnauthorizedException

        token = jwt_encode({
            "id": data.id,
            "name": data.name
        })

        if data is not None:
            return jsonify({
                "type": "authentication",
                "payload": {
                    "token": token
                }
            }), 201
        else:
            raise UnauthorizedException
    except UnauthorizedException:
        return jsonify({
            "type": "error",
            "payload": {
                "message": "email or password incorrect."
            }
        }), 401


@bp.post('/register')
def register():
    try:
        name = request.form.get("name", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if name is None:
            return jsonify({
                "payload": {
                    "type": "error",
                    "message": "kimino namae wa..!"
                }
            }), 400

        if email is None or password is None:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "email or password is no provided."
                }
            }), 400

        password = sha512(password.encode('utf-8')).hexdigest()

        user_check = User.query.filter_by(
            email=email
        ).first()

        if user_check is not None:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "email is already exist."
                }
            }), 400

        user = User(
            id=generate_snowflake(),
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "type": "info",
            "payload": {
                "message": "account successfully created."
            }
        }), 201

    except Exception as e:
        traceback.print_exc(e)
        return jsonify({
            "type": "error",
            "payload": {
                "message": "unexpected error was occurred."
            }
        }), 500
