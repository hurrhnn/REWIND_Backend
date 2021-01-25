import hmac
import json
import base64


def b64_fix(data):
    return data + b"="*((4 - len(data) % 4) if len(data) % 4 != 0 else 0)


def jwt_decode(jwt, secret=b"testsecretkey"):
    body_verify = jwt.rsplit(".", 1)[0]
    header, body, sig = [
        base64.urlsafe_b64decode(b64_fix(data.encode()))
        for data in jwt.split(".")]
    header, body = map(json.loads, (header, body))
    if hmac.digest(secret, body_verify.encode(), digest="sha256") != sig:
        return False
    return body
