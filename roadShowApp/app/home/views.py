# app/home/views.py

from flask import abort, render_template, flash, redirect
from flask_login import login_required, current_user

from sqlalchemy.exc import IntegrityError

from . import home
from .forms import requestForm
from ..models import Roadshows, Requests, Slots, Clients, Attendance
from .. import db
from ..logic.roadshow_logic import Roadshow, Request, Slot, Client
import datetime

# to call the db outside the application
from .. import create_app
import os

config_name = os.getenv('FLASK_CONFIG')


# HOMEPAGE VIEW
@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")


# COMMON USER DASHBOARD
@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")


# ADMIN DASHBOARD VIEW
@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard")


