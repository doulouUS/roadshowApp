from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Required

from ..models import User, Clients, Roadshows, Slots, Attendance
from .. import create_app  # to call the db outside the application

import os

config_name = os.getenv('FLASK_CONFIG')


class requestForm(FlaskForm):
    """
    Create a request
    """
    # db object
    _, app, _ = create_app(config_name=config_name)

    # Which Roadshow
    with app.app_context():
        roadshows = Roadshows.query.all()
    existing_roadshows = [(int(rd.roadshow_id), str(rd.roadshow_name)) for rd in roadshows]
    roadshow = SelectField('Choose a Roadshow to attend', choices=existing_roadshows, validators=[Required()], coerce=int)

    # Which Slot
    with app.app_context():
        slots = Slots.query.all()
    existing_slots = [(int(sl.slot_id), str(sl.slot_name)) for sl in slots]

    # TODO make visible only slot related to roadshow selected
    slot = SelectField('Choose a valid slot ', choices=existing_slots, validators=[Required()],coerce=int)

    # Which company
    with app.app_context():
        companies = Clients.query.all()
    existing_companies = [(int(sl.client_id), str(sl.client_name)) for sl in companies]

    company = SelectField('Company', choices=existing_companies, validators=[Required()], coerce=int)

    # want to host?
    wanna_host = BooleanField('Want to host?', default=False)

    # submit
    submit = SubmitField('Submit Request')

    """
    # Prevent IntegrityError:
    def validate_roadshow(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_slot(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    """
