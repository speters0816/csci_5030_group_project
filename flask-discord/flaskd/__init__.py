import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app. aka Application Factory
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
            )

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
    @app.route("/")
    def index():
        return render_template('login_1.html')

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

        return 'This page has been viewed {} times!'.format(num_views)

    return app
