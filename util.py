import time
import hmac
import json
import base64


def generate_snowflake(session=None):
    from web import db
    from db.models import ModelCreator

    counter = ModelCreator.get_model("counter")
    if session is None:
        # this is flask!
        counter = counter.query.first()
        counter.count += 1
        db.session.commit()
    else:
        # this is websocket!
        counter = session.query(counter).first()
        counter.count += 1
        session.commit()

    custom_timestamp = bin(int(time.time() * 100000))[2:]
    custom_count = ((16 - len(bin(counter.count)[2:])) * "0") + bin(counter.count)[2:]
    return str(int(custom_count + custom_timestamp, 2))


def b64_fix(data):
    return data + b"=" * ((4 - len(data) % 4) if len(data) % 4 != 0 else 0)


def b64_rem(data):
    return data.rstrip("=")


def jwt_decode(jwt):
    body_verify = jwt.rsplit(".", 1)[0]
    header, body, sig = [
        base64.urlsafe_b64decode(b64_fix(data.encode()))
        for data in jwt.split(".")]
    header, body = map(json.loads, (header, body))
    if hmac.digest(secret(True), body_verify.encode(), digest="sha256") != sig:
        return False
    else:
        return body


def jwt_encode(body):
    body_verify = base64.urlsafe_b64encode(bytes('{"alg":"HS256","typ":"JWT"}', "UTF-8")).decode("UTF-8") \
                  + '.' \
                  + base64.urlsafe_b64encode(bytes((json.dumps(body, separators=(',', ':'))), "UTF-8")).decode("UTF-8")
    sig = base64.urlsafe_b64encode(hmac.digest(secret(True), body_verify.rstrip("=").encode(), digest="sha256"))
    return b64_rem(body_verify) + '.' + b64_rem(sig.decode("UTF-8"))


def secret(sig=False):
    return jwt_encode({"id": 0, "name": "Admin", "profile": None}) if not sig else "1084633200".encode()
