import os
import time
from flask import Flask, render_template, g, session, redirect, url_for, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from markupsafe import escape

def create_app(test_config=None):
    # create and configure the app. aka Application Factory
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            )
    socketio = SocketIO(logger=True,engineio_logger=True)
    socketio.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure instance folder exists. Where app instance kept. Not tracked by git.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register db connection with app
    from . import db
    db.init_app(app)


    from . import auth
    app.register_blueprint(auth.bp)

    @app.route("/")
    def index():
        """Redirect user to 'home' room """
        return redirect("/Home")

    @app.route("/<room_id>")
    @auth.login_required
    def change_room(room_id):
        room_id=escape(room_id)
        member_header = "Members"
        
        # Show direct messages on Home page or Member list in specific room
        if room_id == "Home":
            member_header="Direct Messages"
        
        username = g.user["username"] # Grabs username from database fetch stored in g upon user request of the page
                                      # Stored in auth.py
        return render_template('layout.html',username=username,room_id=room_id,member_header=member_header)

    #Logout redirects to login page
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('auth.login'))
    
    # a simple page that prints the view number
    # index page
    @app.route('/count')
    def simple_view():
        sql_db = db.get_db()

        # Check whether views table has any rows. If empty, intialze new siteViews column to 1
        check = sql_db.execute("SELECT views FROM siteViews WHERE rowid=1"
                ).fetchone()
        if check == None:
            sql_db.execute("INSERT INTO siteViews (views) VALUES (1)")
        else:
            sql_db.execute("UPDATE siteViews SET views = views +1 WHERE rowid=1") # Only update 1 row in db


        sql_db.commit()

        num_views = sql_db.execute("SELECT views FROM siteViews WHERE rowid = 1"
                ).fetchone()[0] #Fetchone returns tuple. 1st element contains row value

        return render_template('index_count.html',content=num_views)
    @app.route('/channels/create', methods=["POST","GET"])
    def create_channel():
        if request.method == "POST":
            for i in request.form["member_1"]:
                print(i)

        
        return(render_template("create_channel.html"))


    #from . import socket
    #app.register_blueprint(socket.bp)
    current_users = {}
    @socketio.on('join')
    def on_join(data):
        room = data["room"]
        username = data["username"]

        # Add room to current_users
        if room not in current_users:
            current_users[room] = []

        # Add username to current users list
        if username not in current_users[room]:
            current_users[room].append(username)

        data["current_users"] = current_users[room]
        data["message"] = username + " has joined " + room + " chat"
        print("current Users: ",current_users)
        join_room(room)
        emit("chat join",data,json=True,to=room)
    
    @socketio.on('message sent')
    def on_message(data):
        print("Recieved! ",str(data))
        data["timestamp"] = time.strftime("%B %d %Y %H:%M:%S %z",time.gmtime())
        print(data["timestamp"])
        room = data["room"]
        emit("chat message",data,json=True,to=room)

    @socketio.on("leave")
    def on_leave(data):
        print("\nUser leave emitted")
        room = data["room"]
        leave_room(room)
        username = data["username"]
        current_users[room].remove(username)
        print("current Users: ",current_users)
        emit("chat leave",data,json=True,to=room)
    
    return app
