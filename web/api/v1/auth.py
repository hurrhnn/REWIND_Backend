import asyncio
import threading
import re
from hashlib import sha512

from flask import Blueprint
from flask import copy_current_request_context
from flask import jsonify
from flask import request
from flask_mailing import Message

from web import db
from web import mail
from web import mail_verify

from db.models import ModelCreator
from util import jwt_encode, generate_snowflake

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

        login_user = ModelCreator.get_model("user").query.filter_by(
            email=email,
            password=sha512(password.encode('utf-8')).hexdigest()
        ).first()

        if login_user is None:
            raise ValueError

        token = jwt_encode({
            "id": login_user.id,
            "name": login_user.name
        })

        return jsonify({
            "type": "auth",
            "payload": {
                "token": token
            }
        }), 201
    except (Exception,):
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

        email_check = ModelCreator.get_model("user").query.filter_by(
            email=email
        ).first()

        if email_check is not None:
            return jsonify({
                "type": "error",
                "payload": {
                    "message": "email is already exist."
                }
            }), 400

        email_key = generate_snowflake()

        # if re.search(r"@[\w.]+", email).group() != "@sunrint.hs.kr":
        #     return jsonify({
        #         "type": "error",
        #         "payload": {
        #             "message": "Invalid email address."
        #         }
        #     }), 400

        for key, value in mail_verify.items():
            if value['email'] == email or value['name'] == name:
                del mail_verify[key]
                break

        mail_verify[email_key] = {'name': name, 'email': email,
                                  'password': sha512(password.encode('utf-8')).hexdigest()}

        @copy_current_request_context
        def send_email():
            async def _():
                await mail.send_message(Message(
                    subject="WIND email verification",
                    recipients=[email],
                    body=f'{request.host_url}api/v1/auth/email_verify/{email_key}',
                ))

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_())
            loop.close()

        thread = threading.Thread(target=send_email)
        thread.start()

        return jsonify({
            "type": "info",
            "payload": {
                "message": "successfully created an account creation request."
            }
        }), 201

    except (Exception,) as e:
        print(e)
        return jsonify({
            "type": "error",
            "payload": {
                "message": "unexpected error was occurred."
            }
        }), 500


@bp.get('/email_verify/<key>')
def verify_email(key):
    try:
        account_info = mail_verify.pop(key)

        user = ModelCreator.get_model("user")(
            id=generate_snowflake(),
            name=account_info['name'],
            email=account_info['email'],
            password=account_info['password']
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "type": "info",
            "payload": {
                "message": "account successfully created."
            }
        }), 201

    except (Exception,):
        return jsonify({
            "type": "error",
            "payload": {
                "message": "The session has expired or does not exist."
            }
        }), 404
