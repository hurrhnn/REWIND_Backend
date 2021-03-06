import json


def get_data(type, payload):
    return json.dumps({
        "type": type,
        "payload": payload
    }).encode("utf-8")


def error(code, reason):
    return get_data("error", {
        "code": code,
        "reason": reason
    })


def chat(type, user_id, chat_id, content):
    return get_data("chat", {
        "type": type,
        "user_id": user_id,
        "chat_id": chat_id,
        "content": content
    })
