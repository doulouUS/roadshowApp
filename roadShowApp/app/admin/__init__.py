# app/admin/__init__.py

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views
import datetime

import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)
# use env to load template(s)

@admin.context_processor
def my_utility_processor():
    """
    Utility function that encloses other subfunctions.
    The interest of doing this is to make the subfunctions available in the html files
    when using the jinja syntax.
    """

    def add_time(start_time, timedelta, format="%H:%M:%S"):
        """

        :param start_time: datetime.datetime object
        :param timedelta: datetime.timedelta object
        :param format: string
        :return: string, formatted time result of start_time + timedelta
        """

        add = start_time + datetime.timedelta(minutes=timedelta)
        return add.strftime(format)

    return dict(add_time=add_time)

