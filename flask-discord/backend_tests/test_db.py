import sqlite3

import pytest
from flaskd.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash

def test_get_email(app):
    with app.app_context():
        db = get_db()
        email = "test@gmail.com"
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()
        assert len(user) != 0

def test_get_uknown_user(app):
    """ Tries to get unkown user from database. Should return an empty list """
    with app.app_context():
        db = get_db()
        email = "sam@gmail.com"
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()
        assert user == None

def test_insert_user(app):
    with app.app_context():
        db = get_db()
        email = "ted@yahoo.com"
        username = "CoolTed"
        db.execute("INSERT INTO user (email,username, password) VALUES (?, ?, ?)", (email, username, generate_password_hash("test"))
                )
        db.commit()
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()

        assert user[1] == email

def test_duplicate_insert(app):
    with app.app_context():
        db = get_db()
        email = "test@gmail.com"
        username = "CoolTom"
        db.execute("INSERT INTO user (email,username,password) VALUES (?, ?, ?)", (email, username, generate_password_hash("test"))
                )
        db.commit()
        
        assert db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()


def test_overlength_username(app):
    with app.app_context():
        db = get_db()
        email = "sam@yahoo.com"
        username = "CoolSammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
        db.execute("INSERT INTO user (email,username, password) VALUES (?, ?, ?)", (email, username, generate_password_hash("test"))
                )
        db.commit()
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)
                ).fetchone()

        assert user[1] == email
