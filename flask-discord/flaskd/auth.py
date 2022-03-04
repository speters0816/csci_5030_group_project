import functools

from flask import ( 
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )

from werkzeug.security import check_password_hash, generate_password_hash

from flaskd.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route("/login",methods=("GET","POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()
        
        pass_check = check_password_hash(user["password"],password)

        if user == None or pass_check == None:
            error = "Incorrect Email and Password Combination!"
        
        if error == None:
            session.clear()
            session["user_id"] = user["id"]

            return redirect(url_for("index"))

        flash(error)

    return render_template("login_1.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone() # Grabs all columns in the user table where user_id is found. Load this in the session

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view
