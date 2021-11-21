from flask import Blueprint

# import here!!
from . import auth


API_VERSION = "v1"
bp = Blueprint(
    name=API_VERSION,
    import_name=API_VERSION,
    url_prefix="/" + API_VERSION
)


bp.register_blueprint(auth.bp)


