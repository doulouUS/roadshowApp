# app/home/views.py

from flask import abort, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from flask import request as req
from sqlalchemy.exc import IntegrityError

from . import request
from .forms import RoadshowChoiceForm, WannaHostForm, ConfirmHostForm
from ..models import Roadshows, Requests, Slots, Clients, Attendance
from .. import db
from ..logic.logic import logic_draft
import datetime

# to call the db outside the application
from .. import create_app
import os
from collections import OrderedDict

config_name = os.getenv('FLASK_CONFIG')

# Global definition of existing Roadshows, Clients and Slots
_, app, _ = create_app(config_name=config_name)  # global db object to query the db

# @request.route('request/roadshow', methods=['GET', 'POST'])
# @login_required
# def request_roadshow():


@request.route('/request/roadshow', methods=['GET', 'POST'])
@login_required
def request_roadshow():
    """
    Handles request submission from the dashboard page
    """

    form = RoadshowChoiceForm()

    if form.validate_on_submit():
        # Retrieve slots corresponding to the roadshow
        slots = Slots.query.filter_by(roadshow=form.roadshow.data.roadshow_id)

        # Sum-up info in a dict: {day:{hour:[hosting_client, nb_available_slots]}}
        # possible days
        # days = sorted(list(set([sl.date_time.date() for sl in slots])))

        # for each day, find hours and corresponding hosting_client and nb_avail_slots
        slots_dict = dict()
        for slot in slots:
            # nb of available slots=nb of attendant - max_nb_clients
            nb_attendant = Attendance.query.filter_by(slot_id=slot.slot_id).count()
            max_nb_clients = slot.max_nb_clients
            nb_available_px = max_nb_clients - nb_attendant
            hosting_client = Clients.query.filter_by(client_id=slot.hosting_client).first()
            # current user is registered or not for the slot
            attendants = [att.attendant_id for att in Attendance.query.filter_by(slot_id=slot.slot_id).all()]
            participate = current_user.client_id in attendants
            print("Participation ", participate)

            # complete slots_dict
            if slot.start_time.date() in slots_dict.keys():
                # complete the ordered dictionnary containing hour:[hosting_client,
                # nb_available_px, slot_id]
                slots_dict[slot.start_time.date()][slot.start_time.time()] = [hosting_client.client_name,
                                                                              nb_available_px,
                                                                              nb_attendant,
                                                                              slot.slot_id,
                                                                              slot.one_to_one,
                                                                              slot.set_aside,
                                                                              participate]
            else:
                # add new key as a day with value an empty OrderedDict to slots_dict dictionnary
                slots_dict[slot.start_time.date()] = {slot.start_time.time(): [hosting_client.client_name,
                                                                               nb_available_px,
                                                                               nb_attendant,
                                                                               slot.slot_id,
                                                                               slot.one_to_one,
                                                                               slot.set_aside,
                                                                               participate]}

        current_user_tier = Clients.query.filter_by(client_id=current_user.client_id).first().tier

        return render_template('request/requestSlot.html', roadshow=form.roadshow.data.roadshow_name,
                               slots_dict=slots_dict,
                               current_user_tier=current_user_tier,
                               title='slots')

    return render_template('request/requestRoadshow.html', form=form, title="Request Roadshow")


@request.route('/request/slot/<param>', methods=['GET', 'POST'])
@login_required
def request_slot(param):  # , one_to_one):
    """
    Select a slot
    :param param, list: param[0] is the slot_id and param[1] is whether a One to One has been requested
        (One-to-one should appear only if possible)
    """
    slot_id = int(param[1:-1].split(', ')[0])
    one_to_one = param[1:-1].split(', ')[1] == 'True'
    print('parammm ', param[1:-1])
    print("one to one or ?", slot_id, one_to_one)
    if one_to_one:  # Requested one-to-one meeting
        # TODO Add here a potential function notifying the syndicate or other
        requested_slot = Slots.query.filter_by(slot_id=slot_id).first()

        # check that the request has not already been satisfied...
        if Attendance.query.filter_by(attendant_id=current_user.client_id) \
                .filter_by(slot_id=requested_slot.slot_id).first():
            flash(message="You are already registered for this slot. Write us if you need further information.")
            return redirect(url_for('request.request_roadshow'))

        # ... OR that it is already under review
        old_request = Requests.query.filter_by(asking_client=current_user.client_id) \
            .filter_by(slot_id=requested_slot.slot_id).first()
        if old_request:
            if old_request.under_review is not None:
                flash(message="We are already processing this request. We will get back to you as soon as possible.")
                return redirect(url_for('request.request_roadshow'))

        # register the booking
        # Attendance
        attendance = Attendance(attendant_id=current_user.client_id, slot_id=slot_id, one_to_one=1)
        db.session.add(attendance)
        db.session.commit()

        # Hosting
        # requested_slot.hosting_client = current_user.client_id
        req_slot = db.session.query(Slots).get(slot_id)
        req_slot.hosting_client = current_user.client_id
        req_slot.one_to_one = 1  # Set the slot to full
        db.session.commit()

        # Register the request
        request = Requests(asking_client=current_user.client_id,
                           slot_id=slot_id,
                           time_of_request=datetime.datetime.now(),
                           willing_to_host=1,
                           under_review=datetime.datetime.now() + datetime.timedelta(minutes=15)
                           )
        db.session.add(request)
        db.session.commit()

        flash("You successfully booked this slot for a One-to-one session. The syndicate will come back to you shortly.")
        return render_template('home/dashboard.html',
                               title='Result')
    else:
        # is there someone hosting
        requested_slot = Slots.query.filter_by(slot_id=slot_id).first()
        print("REQUESTED SLOT IS ", slot_id)
        req_slot = db.session.query(Slots).get(slot_id)  # this one is to modify it

        hosting_client = requested_slot.hosting_client
        hosting_client_name = Clients.query.filter_by(client_id=hosting_client).first().client_name

        # check that the request has not already been satisfied...
        if Attendance.query.filter_by(attendant_id=current_user.client_id)\
                            .filter_by(slot_id=requested_slot.slot_id).first():
            flash(message="You are already registered for this slot. Write us if you need further information.")
            return redirect(url_for('request.request_roadshow'))

        # ... OR that it is under review
        old_request = Requests.query.filter_by(asking_client=current_user.client_id)\
                            .filter_by(slot_id=requested_slot.slot_id).first()

        if old_request:
            if old_request.under_review is not None:
                if old_request.under_review > datetime.datetime.now():
                    # second request but we didn't provide answer by the time limit
                    pass
                else:
                    flash(message="We are already processing this request. We will get back to you as soon as possible.")
                return redirect(url_for('request.request_roadshow'))

        # if nobody is hosting
        if hosting_client == 0:
            # Wanna host form
            form = WannaHostForm()

        # if somebody is hosting already
        else:
            # confirm
            form = ConfirmHostForm()

        if form.validate_on_submit():
            if form.confirm.data == -1 and hosting_client != 0:  # does not want to join knowing that someone is hosting
                flash(message="Please select another slot.")
                return redirect(url_for('request.request_roadshow'))

            else:
                # logic processing
                book_slot, host_slot, delayed = logic_draft(client_id=current_user.client_id,
                                                            willing_to_host=form.confirm.data,
                                                            hosting_client=hosting_client)

                willing_to_host = form.confirm.data
                # TODO use the parameter Requests.under_review to set up deadline to process client's request!
                # Display and Register the outcome
                if delayed == 0:
                    if book_slot == 1:
                        if host_slot == 1:
                            flash(message="You successfully registered for this slot and will host as well")
                            # Attendance
                            attendance = Attendance(attendant_id=current_user.client_id, slot_id=slot_id)
                            db.session.add(attendance)
                            db.session.commit()

                            # Hosting
                            # requested_slot.hosting_client = current_user.client_id
                            req_slot = db.session.query(Slots).get(slot_id)
                            req_slot.hosting_client = current_user.client_id
                            db.session.commit()

                            # Register the request
                            request = Requests(asking_client=current_user.client_id,
                                               slot_id=slot_id,
                                               time_of_request=datetime.datetime.now(),
                                               willing_to_host=willing_to_host,
                                               )
                            db.session.add(request)
                            db.session.commit()

                        elif host_slot == 0:
                            flash(message="You successfully registered for this slot. We will get back to you regarding"
                                          " the host of this event.")
                            # Attendance
                            attendance = Attendance(attendant_id=current_user.client_id, slot_id=slot_id)
                            db.session.add(attendance)
                            db.session.commit()

                            # Register the request: time deadline is added
                            request = Requests(asking_client=current_user.client_id,
                                               slot_id=slot_id,
                                               time_of_request=datetime.datetime.now(),
                                               willing_to_host=willing_to_host,
                                               under_review=datetime.datetime.now() + datetime.timedelta(minutes=30)
                                               )
                            db.session.add(request)
                            db.session.commit()

                    elif book_slot == 0:
                        flash(message="This slot is not available at this moment. Please renew your demand.")

                    else:
                        raise ValueError('book_slot is not 1 or 0')

                elif delayed == 1:
                    if book_slot == 1 and host_slot == 1:
                        flash(message="Your request is under review. We will get back to you as soon as possible.")
                        # Register the request: time deadline is added
                        request = Requests(asking_client=current_user.client_id,
                                           slot_id=slot_id,
                                           time_of_request=datetime.datetime.now(),
                                           willing_to_host=willing_to_host,
                                           under_review=datetime.datetime.now() + datetime.timedelta(minutes=30)
                                           )
                        db.session.add(request)
                        db.session.commit()

                    elif book_slot == 0 and host_slot == 1:
                        flash(message="You successfully registered for this slot. We will get back to you regarding "
                                      "the hosting.")
                        # Attendance
                        attendance = Attendance(attendant_id=current_user.client_id, slot_id=slot_id)
                        db.session.add(attendance)
                        db.session.commit()

                        # Register the request: time deadline is added
                        request = Requests(asking_client=current_user.client_id,
                                           slot_id=slot_id,
                                           time_of_request=datetime.datetime.now(),
                                           willing_to_host=willing_to_host,
                                           under_review=datetime.datetime.now() + datetime.timedelta(minutes=15)
                                           )
                        db.session.add(request)
                        db.session.commit()
                else:
                    raise ValueError("book_slot, host_slot and delayed are not either 1 or 0.")

                return render_template('home/dashboard.html',
                                       title='Result')

        return render_template('request/requestHosting.html',
                               slot_name=req_slot.slot_name,
                               hosting_client=hosting_client,
                               hosting_client_name=hosting_client_name,
                               form=form,
                               title="Hosting")
