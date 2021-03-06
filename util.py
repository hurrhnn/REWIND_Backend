import hmac
import json
import base64


def b64_fix(data):
    return data + b"=" * ((4 - len(data) % 4) if len(data) % 4 != 0 else 0)


def b64_rem(data):
    return data.rstrip("=")


def jwt_decode(jwt, secret=b"testsecretkey"):
    body_verify = jwt.rsplit(".", 1)[0]
    header, body, sig = [
        base64.urlsafe_b64decode(b64_fix(data.encode()))
        for data in jwt.split(".")]
    header, body = map(json.loads, (header, body))
    if hmac.digest(secret, body_verify.encode(), digest="sha256") != sig:
        return False
    print(jwt_encode(body))
    return body


def jwt_encode(body, secret=b"testsecretkey"):
    body_verify = base64.urlsafe_b64encode(bytes('{"alg":"HS256","typ":"JWT"}', "UTF-8")).decode("UTF-8") \
                  + '.' \
                  + base64.urlsafe_b64encode(bytes((json.dumps(body, separators=(',', ':'))), "UTF-8")).decode("UTF-8")
    sig = base64.urlsafe_b64encode(hmac.digest(secret, body_verify.rstrip("=").encode(), digest="sha256"))
    return b64_rem(body_verify) + '.' + b64_rem(sig.decode("UTF-8"))
