from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.fields import BooleanField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, Required

from ..models import User, Clients, Roadshows, Slots, Attendance
from .. import create_app  # to call the db outside the application

import os

config_name = os.getenv('FLASK_CONFIG')


class RoadshowChoiceForm(FlaskForm):
    """
    Create a form to select a roadshow before choosing a slot
    """
    roadshow = QuerySelectField(query_factory=lambda: Roadshows.query.all(),
                                get_label="roadshow_name")
    submit = SubmitField('Next')


class WannaHostForm(FlaskForm):
    """
    Create a form to say whether or not the client wants to host.
    """
    confirm = RadioField("Do you want to host this roadshow?", choices=[(1, 'Yes'), (-1, 'No')],
                         coerce=int,
                         validators=[Required(message="Please select one option.")])

    submit = SubmitField('Submit your request.')


class ConfirmHostForm(FlaskForm):
    """
    Create a form to confirm if client wanna join when somebody is hosting
    """
    confirm = RadioField("Do you still want to join?", choices=[(1, 'Yes'), (-1, 'No')],
                         coerce=int,
                         validators=[Required(message="Please select one option.")])
    submit = SubmitField('Submit your request.')



