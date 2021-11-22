import traceback
from hashlib import sha512
from random import choice

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import session
from flask_mailing import Mail, Message

from db.models import ModelCreator
from util import jwt_encode, generate_snowflake
from web import db
from web.api.error import UnauthorizedException
from web import mail

import re

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

        data = ModelCreator.get_model("user").query.filter_by(
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
                "type": "auth",
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
async def register():
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

        user_check = ModelCreator.get_model("user").query.filter_by(
            email=email
        ).first()

        if user_check is not None:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "email is already exist."
                }
            }), 400

        email_key = generate_snowflake()
        if re.search("@[\w.]+", email).group() != "@sunrint.hs.kr":
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "Invalid email address."
                }
            }), 400

        session['user_info'] = {'name':name, 'email':email, 'password':password, 'email_key':email_key}

        message = Message(
            subject="WIND MAIL TEST",
            recipients=[email],
            body=f'/api/v1/auth/email_verify/{email_key}',
            )

        await mail.send_message(message)

        return jsonify({
            "type": "info",
            "payload": {
                "message": "account successfully created."
            }
        }), 201

    except Exception as e:
        print(e)
        traceback.print_exc(e)
        return jsonify({
            "type": "error",
            "payload": {
                "message": "unexpected error was occurred."
            }
        }), 500

@bp.get('/email_verify/<key>')
def email_verify(key):
    try:
        user_info = session['user_info']
        if user_info['email_key'] == key:

            user = ModelCreator.get_model("user")(
                    id=generate_snowflake(),
                    name=user_info['name'],
                    email=user_info['email'],
                    password=user_info['password']
                )

            db.session.add(user)
            db.session.commit()
            return jsonify({
                "type": "info",
                "payload": {
                    "message": "account successfully created."
                }
            }), 201

        else:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "unexpected error was occurred."
                }
            }), 500
    except:
        return jsonify({
            "type": "error",
            "payload": {
                "message": "unexpected error was occurred."
            }
        }), 500
