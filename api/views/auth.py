from flask import Blueprint

callname = __name__.rsplit(".", 1)[-1]

bp = Blueprint(
    name=callname,
    import_name=__name__,
    url_prefix=f"/{callname}"
)


@bp.route('/test')
def test():
    return "Hello, World!"
