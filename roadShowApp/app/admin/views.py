#

# app/admin/views.py

from flask import request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import admin
from .forms import ClientForm, RoadshowForm, SlotForm, RoadshowEditForm
from .. import db
from ..models import Clients, Roadshows, Slots

import datetime

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)


# Clients Views
@admin.route('/clients', methods=['GET', 'POST'])
@login_required
def list_clients():
    """
    List all clients
    """
    check_admin()

    clients = Clients.query.all()

    return render_template('admin/clients/clients.html',
                           clients=clients, title="Clients")


@admin.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    """
    Add a client to the database
    """
    check_admin()

    add_cli = True

    form = ClientForm()  # SlotsChoiceForm(slots_dict={})
    if form.validate_on_submit():
        client = Clients(client_name=form.client_name.data,
                         location=form.location.data,
                         tier=form.tier.data)
        try:
            # add client to the database
            db.session.add(client)
            db.session.commit()
            flash('You have successfully added a new client.')
        except:
            # in case client name already exists
            flash('Error: client name already exists.')

        # redirect to clients page
        return redirect(url_for('admin.list_clients'))

    # load client template
    return render_template('admin/clients/client.html', action="Add",
                           add_cli=add_cli, form=form,
                           title="Add Client")


@admin.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    """
    Edit a client
    """
    check_admin()

    add_cli = False

    client = Clients.query.get_or_404(id)
    form = ClientForm(obj=client)
    if form.validate_on_submit():

        client.client_name = form.client_name.data
        client.location = form.location.data
        db.session.commit()
        flash('You have successfully edited the client.')

        # redirect to the clients page
        return redirect(url_for('admin.list_clients'))

    form.location.data = client.location
    form.client_name.data = client.client_name
    return render_template('admin/clients/client.html', action="Edit",
                           add_cli=add_cli, form=form,
                           client=client, title="Edit Client")


@admin.route('/clients/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_client(id):
    """
    Delete a client from the database
    """
    check_admin()

    client = Clients.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('You have successfully deleted the client.')

    # redirect to the clients page
    return redirect(url_for('admin.list_clients'))

    return render_template(title="Delete Client")

# Roadshows Views


@admin.route('/roadshows')
@login_required
def list_roadshows():
    check_admin()
    """
    List all roadshows
    """
    roadshows = Roadshows.query.all()
    return render_template('admin/roadshows/roadshows.html',
                           roadshows=roadshows, title='Roadshows')


@admin.route('/roadshows/add', methods=['GET', 'POST'])
@login_required
def add_roadshow():
    """
    Add a roadshow to the database
    """
    # TODO This view and the next one are ugly! They mix up WTFforms and normal html form...
    # TODO ...and use hacky tricks to try to get information from one page to another => BAD
    # TODO Ideally: create a dynamic (by passing its class definition, variables)...
    # TODO ...WTFform (I didn't find out how yet) and define a macro...
    # TODO ... for creating a custom display as shown here: http://flask.pocoo.org/docs/0.12/patterns/wtforms/
    check_admin()

    add_roads = True

    form = RoadshowForm()
    if form.validate_on_submit():
        roadshow = Roadshows(roadshow_name=form.roadshow_name.data,
                             start_time=form.start_time.data,
                             end_time=form.end_time.data,
                             meeting_duration=form.meeting_duration.data,
                             time_btw_meetings=form.time_btw_meetings.data,
                             lunch_start_time=form.lunch_start_time.data,
                             lunch_end_time=form.lunch_end_time.data
                             )

        try:
            # add roadshow to the database
            # TODO: By adding the roadshow in the database at this point, we should avoid pressing precedent button...
            # TODO: ...indeed, because the roadshow is now registered, impossible to create another one with the
            # TODO: same name

            # TODO: possible fix: delete the new roadshow when precedent button is used.
            db.session.add(roadshow)
            db.session.commit()
            flash('You have successfully added a new roadshow.')
        except:
            # in case roadshow name already exists
            flash('Error: roadshow name already exists.')

        # Prepare the data needed to format the slots
        morning_time = roadshow.lunch_start_time - roadshow.start_time
        afternoon_time = roadshow.end_time - roadshow.lunch_end_time

        nb_morning_slot = morning_time // datetime.timedelta(minutes=roadshow.meeting_duration
                                                                     + roadshow.time_btw_meetings
                                                             )
        nb_afternoon_slot = afternoon_time // datetime.timedelta(minutes=roadshow.meeting_duration
                                                                         + roadshow.time_btw_meetings
                                                                 )

        list_morning_times = [form.start_time.data
                              + i * (datetime.timedelta(minutes=form.meeting_duration.data)
                              + datetime.timedelta(minutes=form.time_btw_meetings.data))

                              for i in range(0, nb_morning_slot)]

        list_afternoon_times = [form.lunch_end_time.data
                              + i * (datetime.timedelta(minutes=form.meeting_duration.data)
                              + datetime.timedelta(minutes=form.time_btw_meetings.data))
                                + datetime.timedelta(minutes=form.time_btw_meetings.data)

                              for i in range(0, nb_afternoon_slot)]

        # forms needed for every slots
        nb_day = form.number_days.data
        nb_slots = nb_day*(1 + len(list_morning_times) + len(list_afternoon_times))

        # drop down list to select client
        # client_selection_field = [SelectClientForm() for _ in range(0, nb_day*nb_slots)]
        client_list = Clients.query.all()

        paired_list_morning = {t:s for t, s in zip(list_morning_times, range(0, len(list_morning_times)))}
        paired_list_afternoon = {t:s for t, s in zip(list_afternoon_times,
                                                     range(len(list_morning_times),
                                                           len(list_morning_times)+len(list_afternoon_times))
                                                     )}

        return render_template('admin/slots/smart_slots.html',
                               roadshow=roadshow,
                               list_morning_times=list_morning_times,
                               list_afternoon_times=list_afternoon_times,
                               paired_list_morning=paired_list_morning,
                               paired_list_afternoon=paired_list_afternoon,
                               nb_day=nb_day,
                               client_list=client_list,
                               # client_selection_field=client_selection_field,
                               nb_slots=nb_slots
                               )

    # load roadshows template
    return render_template('admin/roadshows/roadshow.html',
                           add_roads=add_roads,
                           form=form,
                           title='Add Roadshow')


@admin.route('/roadshows/add/result/<int:roadshow_id>', methods=['POST', 'GET'])
@login_required
def add_smart_slot(roadshow_id):
    """
    Build an automated schedule with parameters entered into roadshow

    Structure of the input's names from html forms:
    FOR THE DAY
    day* with * integer designating the day in order of creation

    FOR THE SLOTS
    slot_name_*_% with % slot number (integer in order of appearance) for day *
    max_nb_clients_*_%  ...
    start_time_*_%  ...
    end_time_*_%  ...
    set_aside_*_%  ...


    :param roadshow: Roadshows object (obtained by executing Roadshows.query.all())
    :param nb_day: int, number of days the roadshow will take place
    :return:
    """
    check_admin()
    print("roadshow_id = ", roadshow_id)
    print('form content ', list(request.form.keys()))

    # retrieve number of days
    days = [day for day in list(request.form.keys()) if 'day' in day]  # list of strings
    print("days outta camption ", days)
    # retrieve number of slots per day (same for all days)
    # +1 because indexing from 0: do not count lunch
    nb_slot = max([int(slot[-1])+1 for slot in list(request.form.keys()) if 'slot_name_1_' in slot])

    print("number of slots per day ", nb_slot)

    print("__ slot sum-up __")
    # for each day
    for day in days:
        print("DAY "+day[-1])
        # for each slot this day out of lunch
        for sl in range(0, nb_slot):
            print("*** SLOT ***")
            print("date ", request.form[day])  # YYYY-MM-DD

            slot_name = request.form['slot_name_'+day[-1]+'_'+str(sl)]
            print('slot_name ', slot_name)

            hosting_client = request.form["host_name_"+day[-1]+'_'+str(sl)]
            print("hosting client ", hosting_client)

            max_nb_clients = request.form['max_nb_clients_'+day[-1]+'_'+str(sl)]
            print('max_nb_clients ', max_nb_clients)

            # (1) TODO Understand why half of the time %H:%M:%S works and other half %H:%M works too...
            # TODO for now we fix this by catching an exception...
            try:
                start_time = datetime.datetime.strptime(request.form[day]
                                                        + " "
                                                        + request.form['start_time_'+day[-1]+'_'+str(sl)],
                                                        "%Y-%m-%d %H:%M")
            except:
                start_time = datetime.datetime.strptime(request.form[day]
                                                        + " "
                                                        + request.form['start_time_'+day[-1]+'_'+str(sl)],
                                                        "%Y-%m-%d %H:%M:%S")

            print('start_time ', start_time)
            try:
                end_time = datetime.datetime.strptime(request.form[day]
                                                      + " "
                                                      + request.form['end_time_'+day[-1]+'_'+str(sl)],
                                                      "%Y-%m-%d %H:%M")
            except:
                end_time = datetime.datetime.strptime(request.form[day]
                                                      + " "
                                                      + request.form['end_time_'+day[-1]+'_'+str(sl)],
                                                      "%Y-%m-%d %H:%M:%S")

            try:
                test = request.form['set_aside_'+day[-1]+'_'+str(sl)]
                set_aside = 1
            except:  # if error means the name of the checkbox is not in the form.keys(), so it's not selected
                set_aside = 0
            print('set_aside ', set_aside)

            # Create
            slot = Slots(slot_name=slot_name,
                         hosting_client=hosting_client,
                         roadshow=roadshow_id,
                         max_nb_clients=max_nb_clients,
                         start_time=start_time,
                         end_time=end_time,
                         set_aside=set_aside
                         )
            # add slot to the database
            db.session.add(slot)
            db.session.commit()
            # flash('You have successfully added a new slot.')



        # for lunch slot
        print("__ LUNCH __")
        slot_name = request.form['slot_name_lunch_' + day[-1]]
        print('slot_name ', slot_name)

        hosting_client = request.form["host_name_lunch_" + day[-1]]
        print("hosting client ", hosting_client)

        max_nb_clients = request.form['max_nb_clients_lunch_' + day[-1]]
        print('max_nb_clients ', max_nb_clients)

        # (2) TODO Understand why half of the time %H:%M:%S works and other half %H:%M works too...
        try:
            start_time = datetime.datetime.strptime(request.form[day]
                                                    + " "
                                                    + request.form['start_time_lunch_' + day[-1]],
                                                    "%Y-%m-%d %H:%M")
        except:
            start_time = datetime.datetime.strptime(request.form[day]
                                                    + " "
                                                    + request.form['start_time_lunch_' + day[-1]],
                                                    "%Y-%m-%d %H:%M:%S")

        print('start_time ', start_time)
        try:
            end_time = datetime.datetime.strptime(request.form[day]
                                                  + " "
                                                  + request.form['end_time_lunch_' + day[-1]],
                                                  "%Y-%m-%d %H:%M")
        except:
            end_time = datetime.datetime.strptime(request.form[day]
                                                  + " "
                                                  + request.form['end_time_lunch_' + day[-1]],
                                                  "%Y-%m-%d %H:%M:%S")
        print('end_time ', end_time)

        try:
            test = request.form['set_aside_lunch_' + day[-1]]
            set_aside = 1
        except:  # if error means the name of the checkbox is not in the form.keys(), so it's not selected
            set_aside = 0
        print('set_aside_lunch ', set_aside)

        # Create and add slot to the db
        slot = Slots(slot_name=slot_name,
                     hosting_client=hosting_client,
                     roadshow=roadshow_id,
                     max_nb_clients=max_nb_clients,
                     start_time=start_time,
                     end_time=end_time,
                     set_aside=set_aside
                     )
        try:
            # add slot to the database
            db.session.add(slot)
            db.session.commit()

        except:
            # in case client name already exists
            flash('Error: slot name already exists.')
            # TODO Roll back roadshow as it has been added to the db before
            # TODO change datetime type for roadshow's start_time, start_lunch_time, end_lunch_time and end_time
            # TODO only time is interesting, not the date part
            # redirect to roadshows page
            return redirect(url_for('admin.list_roadshows'))

    flash('You have successfully planned the roadshow.')
    return redirect(url_for('admin.list_roadshows'))

    return render_template('home/dashboard.html')


@admin.route('/roadshows/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_roadshow(id):
    """
    Edit a roadshow
    """
    check_admin()

    add_roads = False

    roadshow = Roadshows.query.get_or_404(id)
    form = RoadshowEditForm(obj=roadshow)
    if form.validate_on_submit():
        roadshow.roadshow_name = form.roadshow_name.data
        roadshow.start_time = form.start_time.data,
        roadshow.end_time = form.end_time.data,
        roadshow.meeting_duration = form.meeting_duration.data,
        roadshow.time_btw_meetings = form.time_btw_meetings.data,
        roadshow.lunch_start_time = form.lunch_start_time.data,
        roadshow.lunch_end_time = form.lunch_end_time.data

        db.session.add(roadshow)
        db.session.commit()
        flash('You have successfully edited the roadshow.')

        # redirect to the roadshows page
        return redirect(url_for('admin.list_roadshows'))

    form.roadshow_name.data = roadshow.roadshow_name
    return render_template('admin/roadshows/roadshow.html', add_roads=add_roads,
                           form=form, title="Edit Roadshow")


@admin.route('/roadshow/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_roadshow(id):
    """
    Delete a roadshow from the database
    """
    check_admin()

    roadshow = Roadshows.query.get_or_404(id)
    db.session.delete(roadshow)
    db.session.commit()
    flash('You have successfully deleted the roadshow.')

    # redirect to the roadshows page
    return redirect(url_for('admin.list_roadshows'))

    # return render_template(title="Delete Roadshow")


@admin.route('/slots')
@login_required
def list_slots():
    """
    List all employees
    """
    check_admin()

    slots = Slots.query.all()

    # map roadshow_id and roadshow_name
    roadshows = Roadshows.query.all()
    roadshow_id_to_name = {rd.roadshow_id:rd.roadshow_name for rd in roadshows}

    # map client_id and client_name
    clients = Clients.query.all()
    client_id_to_name = {cl.client_id:cl.client_name for cl in clients}
    return render_template('admin/slots/slots.html',
                           roadshow_id_to_name=roadshow_id_to_name,
                           client_id_to_name=client_id_to_name,
                           slots=slots, title='Slots')


@admin.route('/slot/lookup/<int:id>', methods=['GET', 'POST'])
@login_required
def lookup_slots(id):
    """
    List slots associated with a roadshow (given by id)
    """
    check_admin()

    slots = Slots.query.filter_by(roadshow=id).all()
    # map roadshow_id and roadshow_name
    roadshows = Roadshows.query.all()
    roadshow_id_to_name = {rd.roadshow_id:rd.roadshow_name for rd in roadshows}

    # map client_id and client_name
    clients = Clients.query.all()
    client_id_to_name = {cl.client_id:cl.client_name for cl in clients}
    return render_template('admin/slots/slots.html',
                           roadshow_id_to_name=roadshow_id_to_name,
                           client_id_to_name=client_id_to_name,
                           slots=slots, title='Slots')


@admin.route('/slots/add', methods=['GET', 'POST'])
@login_required
def add_slot():
    """
    Add a slot to the database
    """
    check_admin()

    add_sl = True

    form = SlotForm()
    if form.validate_on_submit():
        slot = Slots(slot_name=form.slot_name.data,
                     hosting_client=form.hosting_client.data.client_id,
                     roadshow=form.roadshow.data.roadshow_id,
                     max_nb_clients=form.max_nb_clients.data,
                     start_time=form.start_time.data,
                     end_time=form.end_time.data,
                     set_aside=form.set_aside.data
        )
        try:
            # add client to the database
            db.session.add(slot)
            db.session.commit()
            flash('You have successfully added a new slot.')
        except:
            # in case client name already exists
            flash('Error: slot name already exists.')

        # redirect to clients page
        return redirect(url_for('admin.list_slots'))

        # load client template
    return render_template('admin/slots/slot.html', action="Add",
                           add_cli=add_sl, form=form,
                           title="Add Slot")


@admin.route('/slots/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_slot(id):
    """
    Assign a roadshow to a slot
    """
    check_admin()

    add_sl = False

    slot = Slots.query.get_or_404(id)

    form = SlotForm(obj=slot)
    if form.validate_on_submit():

        slot.hosting_client = form.hosting_client.data.client_id
        slot.roadshow = form.roadshow.data.roadshow_id
        slot.max_nb_clients = form.max_nb_clients.data  # roadshows or slots?
        slot.slot_name = form.slot_name.data
        slot.start_time = form.start_time.data
        slot.end_time = form.end_time.data
        slot.set_aside = form.set_aside.data

        db.session.add(slot)
        db.session.commit()
        flash('You have successfully edited a slot.')

        # redirect to the roles page
        return redirect(url_for('admin.lookup_slots', id=slot.roadshow))

    return render_template('admin/slots/slot.html',
                           add_sl=add_sl,
                           slot=slot, form=form,
                           title='Assign Slot')


