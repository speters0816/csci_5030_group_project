import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """ Connect to sqlite3 database in current app instance.
        Returns db connection for modifying columns/rows in db"""
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """ Helper function to close database connection """
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """ Function used on the command line to create new
        database instance """
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the exisiting data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """ Add commnad line function for init-db command. Tells app to close database on exit """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


