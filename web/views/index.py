
from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template


bp = Blueprint(
    name="index",
    import_name="index",
    url_prefix="/"
)


@bp.route('/')
def index():
    if 'logined' not in session:
        return redirect(url_for('index.login'))
    print(session['logined'])
    return render_template('index.html')


@bp.route('/login')
def login():
    return render_template('login.html')


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/logout')
def logout():
    # flash("Logout!!")
    session['logined'] = False
    return redirect(url_for('index.index'))
