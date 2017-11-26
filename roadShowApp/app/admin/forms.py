
# app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, NumberRange
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError

from ..models import Clients, Roadshows, Slots


class ClientForm(FlaskForm):
    """
    Form for admin to add or edit a client
    """
    client_name = StringField('Client Name', validators=[DataRequired()])
    location = StringField('Client\'s address', validators=[DataRequired()])
    tier = IntegerField('Client\'s tier', validators=[DataRequired(), AnyOf(values={1, 2, 3},
                                                                            message="Provide a tier among 1, 2 or 3.")])
    submit = SubmitField('Submit')

# Check that typed name does not exist in the db
def check_unique_roadshow(form, field):
    roadshows = Roadshows.query.all()
    if field.data in [rd.roadshow_name for rd in roadshows]:
        raise ValidationError('This Roadshow name is already taken.')

""" THERE ARE 2 ROADSHOW FORMS: ADD and EDIT. Don't Forget to modify both!"""
class RoadshowForm(FlaskForm):
    """
    Form for admin to add or edit a roadshow
    """

    roadshow_name = StringField('Roadshow Name', validators=[DataRequired(), check_unique_roadshow])

    start_time = DateTimeField("Start Time", validators=[DataRequired()])
    end_time = DateTimeField("End Time (choose the same day as in Start Time)", validators=[DataRequired()])
    meeting_duration = IntegerField("Meeting Duration (minutes)", validators=[DataRequired(), NumberRange(min=0, max=180)])
    time_btw_meetings = IntegerField("Time between meetings (minutes)", validators=[DataRequired(),
                                                                          NumberRange(min=0, max=180)])
    lunch_start_time = DateTimeField("Lunch Start Time", validators=[DataRequired()])
    lunch_end_time = DateTimeField("Lunch End Time", validators=[DataRequired()])

    number_days = IntegerField("How many days would you like to set for this roadshow?", validators=[DataRequired()])

    submit = SubmitField('Submit')


class RoadshowEditForm(FlaskForm):
    """
    Form for admin to edit a roadshow
    """

    roadshow_name = StringField('Roadshow Name', validators=[DataRequired()])

    start_time = DateTimeField("Start Time", validators=[DataRequired()])
    end_time = DateTimeField("End Time (choose the same day as in Start Time)", validators=[DataRequired()])
    meeting_duration = IntegerField("Meeting Duration (minutes)", validators=[DataRequired(), NumberRange(min=0, max=180)])
    time_btw_meetings = IntegerField("Time between meetings (minutes)", validators=[DataRequired(),
                                                                          NumberRange(min=0, max=180)])
    lunch_start_time = DateTimeField("Lunch Start Time", validators=[DataRequired()])
    lunch_end_time = DateTimeField("Lunch End Time", validators=[DataRequired()])

    number_days = IntegerField("How many days would you like to set for this roadshow?", validators=[DataRequired()])

    submit = SubmitField('Submit')


class SelectClientForm(FlaskForm):
    """
    Form for creation of Slots after creating the Roadshows
    """
    client = QuerySelectField(query_factory=lambda: Clients.query.all(),
                              get_label="client_name")


class SlotForm(FlaskForm):
    """
    Form for admin to assign slots to Roadshows
    """
    roadshow = QuerySelectField(query_factory=lambda: Roadshows.query.all(),
                                get_label="roadshow_name")

    # foreign
    hosting_client = QuerySelectField(query_factory=lambda: Clients.query.all(),
                                      get_label="client_name")

    # attributes
    max_nb_clients = IntegerField('Maximum Number of Clients at this Roadshow ',
                                  validators=[DataRequired(),
                                              NumberRange(min=1, max=100,
                                                          message="Input an integer between 1 and 100")
                                              ]
                                  )
    slot_name = StringField('Slot Name', validators=[DataRequired()])
    start_time = DateTimeField("Date and Time", validators=[DataRequired()])
    end_time = DateTimeField("Date and Time", validators=[DataRequired()])
    set_aside = BooleanField("Set Slot Aside of Booking?")

    submit = SubmitField('Submit')

