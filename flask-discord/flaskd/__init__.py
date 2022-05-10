import os
import time
from flask import Flask, render_template, g, session, redirect, url_for, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from markupsafe import escape
import pickle
import calendar

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
        return redirect("/Random")

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

    def save_history(obj,outPath):
        """Saves obj as binary file with pickle to filepath """
        
        # Save chat history
        with open(outPath,"wb")as f :
            pickle.dump(obj,f)
    
    print("chat pickle saved!")

    def load_history(objPath):
        """Loads pickled object """
        with open(objPath,"rb") as f:
            message_history = pickle.load(f)
        
        return message_history

    outFile= os.path.join(os.getcwd(),"flaskd","history","chat_history")
    # Load message history if available
    if os.path.isfile(outFile):
        message_history = load_history(outFile)
        print("loaded chat history from pickle!")
        print(type(message_history))
    else:
        message_history = {}

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

        # Add message to chat history 
        if room not in message_history:
            message_history[room] = []

        data["current_users"] = current_users[room]
        data["message"] = username + " has joined " + room + " chat"
        data["message_history"] = message_history[room]
        
        #print(data["message_history"])
        print("current Users: ",current_users)
        join_room(room)
        emit("chat join",data,json=True,to=room)


    @socketio.on('message sent')
    def on_message(data):
        new_message = data["message"]
        print("Recieved! ",str(data))
        time_format = "%B %d %Y %H:%M:%S %z"
        data["timestamp"] = time.strftime(time_format,time.gmtime())
        print(data["timestamp"])
        room = data["room"]
        
        # Grab last message before appending new
        lenRoomHistory = len(message_history[room])
        print("Room: ",room," len: ",lenRoomHistory)
        if lenRoomHistory != 0:
            data["previous_message"] = message_history[room][lenRoomHistory-1]
        else:
           data["previous_message"] = ["Null","April 28 0001 03:12:15 -0600","Null"]

        newMsg_gmtime = time.strptime(data["timestamp"],time_format)
        prevMsg_gmtime = time.strptime(data["previous_message"][1],time_format)
        prevUser = data["previous_message"][0]
        newUser = data["username"]
        print("TIme diff: ",calendar.timegm(newMsg_gmtime) - calendar.timegm(prevMsg_gmtime))
        # If continuation of user message, append to history rather than create new entry
        if (calendar.timegm(newMsg_gmtime) - calendar.timegm(prevMsg_gmtime) < 300 and newUser == prevUser):
            print("working!")
            message_history[room][lenRoomHistory-1][-1].append(new_message)
        else:
            message = [data["username"],data["timestamp"],[data["message"]] ] # This doesn't actually change the original user message. Updates it for history
            message_history[room].append(message)

        save_history(message_history,outFile)
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
