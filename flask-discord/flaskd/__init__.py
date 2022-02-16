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

    # a simple page that prints the view number
    # index page
    @app.route('/')
    def simple_view():
        return 'This page needs to print the views!'

    return app
