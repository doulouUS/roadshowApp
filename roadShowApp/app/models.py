# models.py created on 9-10-17

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import sys
sys.path.append(".")
from app import db, login_manager

"""
Each class creates the equivalent of a table in mysql, with the column names, relationship (one-to-many etc.)

To create the db at first in terminal
    All the db setup is made in the file: roadshowApp/instance/config.py

    go in current directory roadshowApp/
    activate environment (source path/to/env/activate)
    run: flask db init (create migrations folder, that will contain all the db versions)
    (*) create a migration: flask db migrate
    (*) implement the migration: flask db upgrade

Whenever the scheme of the db is changed, you only need to run the (*) phases.
"""

class User(UserMixin, db.Model):
    """
    Create an Employee table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Employee: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Clients(db.Model):
    """
    Create a Client table
    """
    __table_name__ = "clients"

    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(300), nullable=False, unique=True)
    location = db.Column(db.String(300), nullable=False, unique=True)
    tier = db.Column(db.Integer, nullable=False)

    # One to many relationship
    attendance = db.relationship('Slots', backref='clients', lazy=True)

    def __repr__(self):
        return '<Client: {}>'.format(self.client_name)


class Attendance(db.Model):
    """
    Create an Attendance table:
    """
    __table_name__ = "attendance"

    # primary
    attendance_id = db.Column(db.Integer, primary_key=True)

    # foreign
    attendant_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.slot_id'))
    one_to_one = db.Column(db.Boolean, default=0)


    def __repr__(self):
        return '<Attendance: {} is registered for slot {}>'.format(self.attendant_id, self.slot_id)


class Requests(db.Model):
    """
    Create a Requests table
    """
    __table_name__ = "requests"

    # primary
    request_id = db.Column(db.Integer, primary_key=True)

    # foreign
    asking_client = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.slot_id'))

    # attributes
    time_of_request = db.Column(db.DateTime, nullable=False)
    willing_to_host = db.Column(db.Boolean, default=False)
    under_review = db.Column(db.DateTime)
    processed = db.Column(db.Boolean, default=False)

    # foreign not defined yet
    # slot_id = db.relationship('Slots', backref='requests', lazy=True)

    def __repr__(self):
        return '<Request: from {} for {} slot>'.format(self.asking_client, self.slot_id)


class Roadshows(db.Model):
    """
    Create a Roadshow table
    """
    __table_name__ = "roadshows"

    # primary
    roadshow_id = db.Column(db.Integer, primary_key=True)

    # attribute
    roadshow_name = db.Column(db.String(300), nullable=False, unique=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    meeting_duration = db.Column(db.Integer, nullable=False)
    time_btw_meetings = db.Column(db.Integer, nullable=False)
    lunch_start_time = db.Column(db.DateTime, nullable=False)
    lunch_end_time = db.Column(db.DateTime, nullable=False)

    slots = db.relationship("Slots", cascade="all, delete-orphan")

    def __repr__(self):
        return '<Roadshow: {}>'.format(self.roadshow_name)


class Slots(db.Model):
    """
    Create a Slot table
    """

    __tablename__ = 'slots'

    # primary
    slot_id = db.Column(db.Integer, primary_key=True)

    # foreign
    hosting_client = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    roadshow = db.Column(db.Integer, db.ForeignKey('roadshows.roadshow_id'))

    # attributes
    # TODO for robustness, create a group of keys to be unique ex: roadshow - slot_name
    # TODO string of length 300 may be too long for certain platform in deployment phase (ex: pythonanywhere doesn't ...
    # TODO ... support it.
    max_nb_clients = db.Column(db.Integer, nullable=False)
    slot_name = db.Column(db.String(300),nullable=False)  # ,  unique=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    set_aside = db.Column(db.Boolean, default=False)
    one_to_one = db.Column(db.Boolean, default=False)

    attendance = db.relationship("Attendance", cascade="all, delete-orphan")
    requests = db.relationship("Requests", cascade="all, delete-orphan")

