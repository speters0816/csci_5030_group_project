import functools

from flask import ( 
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )

from werkzeug.security import check_password_hash, generate_password_hash

from flaskd.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')
#
@bp.route("/settings",methods=("GET","POST"))
def change_username():
    if request.method == "POST":
        new_username=request.form["uname"]
        email=request.form['email']
        # print(new_username)
        db = get_db()
        db.execute("UPDATE user SET username =? WHERE email=?",(new_username,email))
        db.commit()
        return redirect(url_for("index", room_id="Home"))
    
    return render_template("settings.html")

@bp.route("/login",methods=("GET","POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()
        
        if user == None: 
            error = "Incorrect Email Provided!" 
            
        elif not check_password_hash(user["password"],password):
            error = "Incorrect password!"
            
        if error == None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index", room_id="Home"))

        flash(error)

    return render_template("login_1.html")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """ Registers user from regiseter.html form submission"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        db = get_db()
        error = None

        if not email: # Checking where email and password are empty values. 
            error = "Email is Required!"
        elif not password:
            error = "Password is Required!"
        elif not username:
            error = "Username is Required"
        elif len(username) > 32:
            error = "Error! Username too long. Please make it less than 32 characters long"
            
        if error == None:
            # Check if user already exists
            if db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone() != None:
                error = "Email already registered"
            
            else:
                try:
                    db.execute("INSERT INTO user (email,username, password) VALUES (?, ?, ?)", (email, username, generate_password_hash(password)))

                    db.commit()
                
                except db.IntegrityError:
                    error = "Username {} is already taken.".format(username)

                else:
                    flash("You successfully registered!")
                    return redirect(url_for("auth.login"))

        flash(error)

    return render_template("register_2.html")

@bp.before_app_request
def load_logged_in_user():
    """ Load logged in user information by identifying if session contains the user id. 
        If user logged in, queries database and grabs information"""
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
