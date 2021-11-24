import json


def get_data(_type, payload):
    return json.dumps({
        "type": _type,
        "payload": payload
    }).encode("utf-8")


def authenticate(sess_data, _mutual_users):
    return get_data("auth", {
        "self_user": sess_data['user'],
        "mutual_users": _mutual_users
    })


def heartbeat(payload):
    return get_data("heartbeat", payload)


def error(code, reason):
    return get_data("error", {
        "code": code,
        "reason": reason
    })


def chat(_type, _id, user_id, chat_id, created_at, content):
    return get_data("chat", {
        "type": _type,
        "id": _id,
        "user_id": user_id,
        "chat_id": chat_id,
        "created_at": created_at,
        "content": content
    })


def load(queried_data):
    return json.dumps(queried_data).encode('utf-8')


def mutual_users(_type, name=None):
    return get_data("mutual_users", {
        "type": _type,
        "name": name
    })
