import datetime
import threading  # for several request in the same time
import time

from .. import create_app
from ..models import Roadshows, Requests, Slots, Clients, Attendance

import os

# Homemade modules
# from ..Database import database_toolbox as home_db

# THIS AN OLD LOGIC FILE => not used anywhere (used for the first interface)
# It has Client, Request, Roadshow and Slot classes.
# A roadshow includes as members a list of slot objects.
# A slot has a list of participating clients.


class Client:

    def __init__(self, name, tier, location, client_id):
        # TODO specify location
        self.name = name

        # Read into csv file
        self.tier = tier
        self.location = location
        self.client_id = client_id

    """ ------- Allows respectively: == comparison, != comparison, set making, len() function among others---------"""
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

    """------------------------------------------------------------------------------------------------------------"""

    def display_client(self):
        print("  ")
        print(" ---------------------------------------------------------")
        print("| client's name      | ", self.name)
        print(" ---------------------------------------------------------")
        print("| Tier:              | ", self.tier)
        print(" ---------------------------------------------------------")
        print("| Client's location  | ", self.location)
        print(" ---------------------------------------------------------")

        print("  ")

########################################################################################################


class Slot:

    def __init__(self,
                 start_time,
                 slot_id,
                 hosting_client=Client(name="Choose among the selection",
                                       location="Nobody is hosting yet.",
                                       client_id=0,
                                       tier=0
                                       ),
                 max_client=4,
                 slotname="Give a slot name !"
                 ):
        """
        Define a slot in a roadshow
        :param start_time: datetime.time instance, contains hour, minute, potentially seconds and time zone
        :param hosting_client: /!\ client instance or 0 if non assigned yet /!\  client hosting the slot
        :param roadshow, Roadshow object
        :param max_client: max nb of client attending the slot
        """
        self.start_time = start_time
        self.max_client = max_client
        self.slot_name = slotname
        self.slot_id = slot_id
        # TODO not necessary ?
        # self.roadshow = roadshow


        # protected features that are modified by incoming requests, subject to logic verification
        self._list_clients = []   # no one has booked at first
        self.hosting_client = hosting_client

    """ ------- Allows respectively: == comparison, != comparison, set making, len() function among others---------"""
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

    """------------------------------------------------------------------------------------------------------------"""
    def get_list_clients(self):
        return self._list_clients

    def gethosting_client(self):
        return self.hosting_client

    def assign_slot(self, client):
        """
        Add a client to the slot.
        does NOT mean the client host !

        :param client: client instance
        :return: True if the slot is assigned to the client, False otherwise
        """
        if self.slot_status():
            self._list_clients.append(client)  # update the list of clients participating to the meeting

            print("Slot taking place at ", self.start_time)
            print("has been added a new client: ")
            client.display_client()
            return True
        else:
            print("SLOT FULL")
            return False

    def unassign_slot(self, client):
        """
        Remove a client from the slot, this can only happen when the client refuses to join a slot, because
        he can't host
        :param client:
        :return:
        """

        if client in self._list_clients:
            # remove all occurences of the concerned client
            self._list_clients = [cl for cl in self._list_clients if cl != client]
            print("Slot taking place at ", self.start_time)
            print("has been removed a client: ")
            client.display_client()
            return True

        else:
            if not self._list_clients:
                raise ValueError('self._list_clients empty')
            else:
                raise ValueError('client not in self._list_clients')

    def assign_hosting_client(self, client):
        """
        Assign the location of the slot meeting to the client's location
        Used in Roadshow, which provides security features

        :param client: client instance
        :return: boolean, True if self.hosting_client changed ; False otherwise
        """

        # custom messages
        if self.hosting_client.tier == 0:
            print("/!\ Hosting place assigned for the first time to ")
            client.display_client()

        elif isinstance(self.hosting_client, Client) and self.hosting_client.tier != 0:
            print("KICKED OUT WARNING ! ??")
            print("Previous client hosting ")
            self.hosting_client.display_client()
            print("has been replaced by the following client ")
            client.display_client()
        else:
            raise ValueError('self.hosting_client. Wrong type, expected client')

        self.hosting_client = client
        return True


    def unassign_hosting_client(self):

        if isinstance(self.hosting_client, Client) and self.hosting_client.tier != 0:
            print("KICKED OUT WARNING")
            print("Previous client hosting ")
            self.hosting_client.display_client()
            print("has been replaced by NOBODY ")
            client.display_client()

        else:
            raise ValueError('self.hosting_client. Wrong type, expected client')

        self.hosting_client = Client(name="Choose among the selection",
                                     location="Nobody is hosting yet.",
                                     tier=0,
                                     client_id=0)
        return True


    def slot_status(self):
        """
        Say if there is at least room for one more client in this slot
        :return: True if there is still room for the client ; False otherwise
        """

        if len(self._list_clients) < self.max_client:
            return True

        else:
            return False

    def display_slot(self):
        """
        Give the main info of the slot and enrolled clients
        :return:
        """
        print("###########################################################")
        print("SLOT SUMMARY")
        print("Slot's start time           :", self.start_time)
        try:
            print("Slot's location             :", self.hosting_client.name)
        except:
            print("Slot's location             :", self.hosting_client.location)

        print("Number of enrolled clients  :", len(self._list_clients))
        for i in range(0, len(self._list_clients)):
            print("Client number ", i + 1)
            print(self._list_clients[i].display_client())
        print("###########################################################")

########################################################################################################


class Roadshow:

    def __init__(self, roadshow_name, list_slots, roadshow_id):  #, date):
        """
        Contains all the details of the roadshow known as of now
        :param roadshow_name: str, identifier of the roadshow, can contain the name of the borrower for instance
        :param list_slots: list of slots instance
        :param date: datetime.date object, contains year, month, day"
        """
        self.roadshow_name = roadshow_name
        self.roadshow_id = roadshow_id
        self.list_slots = list_slots
        # self.date = date  # date = datetime.date(year=  , month=  , day=   )

        self.list_requests = []  # contains all the submitted requests

        # Assignment pending requests
        self.tier3_slot_assignment_time_pending = datetime.timedelta(hours=3)  # 3 hours pending
        self.tier2_hosting_assignment_time_pending = datetime.timedelta(hours=2)  # 2 hours pending

    """ ------- Allows respectively: == comparison, != comparison, set making, len() function among others---------"""
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

    """------------------------------------------------------------------------------------------------------------"""

    def get_idx_requested_slot(self, slot):
        """
        Return the index at which slot is in self.list_slots
        :param slot:
        :return: int
        """
        # TODO this is potentially slow
        return self.list_slots.index(slot)

    def record_request(self, r):
        try:
            self.list_requests.append(r)
            return True

        except:
            raise ValueError('self.list_requests. cannot append new request')

    def assign_slot(self, request):
        if request.slot_granted:
            # slot where the client has to be added
            requested_slot = request.slot

            # index of the requested slot in the self.list_slots
            idx_requested_slot = self.get_idx_requested_slot(requested_slot)

            # modify the corresponding slot according to the request
            assignment = self.list_slots[idx_requested_slot].assign_slot(request.client)

            if assignment:
                # write the DB
                # home_db.assign_slot_db(request.slot.slot_id, request.client.client_id, db)

                # print summary of the updated slot
                self.list_slots[idx_requested_slot].display_slot

                return True
            # TODO ELSE: Message on console?

        else:
            raise ValueError("request.slot_granted is False. No permission granted to get this slot!")

    def unassign_slot(self, request):
        """
        Undo slot assignment. This happen when a client refuses to go to a slot he can't host
        :param request: request object to be rolled back
        :param db: MySQLdb object
        :return: True if transaction went well.
        """
        if request.slot_granted:  # remove only if request's client already registered a slot
            # slot where the client has to be added
            requested_slot = request.slot

            # index of the requested slot in the self.list_slots
            idx_requested_slot = self.get_idx_requested_slot(requested_slot)

            # modify the corresponding slot according to the request
            unassignment = self.list_slots[idx_requested_slot].unassign_slot(request.client)

            if unassignment:
                # write the DB
                # home_db.unassign_slot_db(request.slot.slot_id, request.client.client_id, db)

                # print summary of the updated slot
                self.list_slots[idx_requested_slot].display_slot

                return True

            # print summary of the updated slot
            self.list_slots[idx_requested_slot].display_slot

            return True

    def assign_hosting_client(self, request):
        if request.slot_granted:
            # index of the requested slot in the self.list_slots
            idx_requested_slot = self.list_slots.index(request.slot)
            # case where slot has been granted but the client is not granted hosting
            if not request.host_granted:
                print("No permission to host this slot.")

            elif request.host_granted and request.slot in self.list_slots:
                # modify the corresponding slot according to
                assignment = self.list_slots[idx_requested_slot].assign_hosting_client(request.client)

                if assignment:
                    # write the DB
                    # home_db.assign_hosting_client_db(slot_id=request.slot.slot_id ,
                    #                              host_client=request.client.client_id,
                    #                              db=db
                    #                              )
                    pass
            else:
                print("Wrong request, this slot does not exist ")

            # print summary of the updated slot
            self.list_slots[idx_requested_slot].display_slot

        else:
            print("Make sure you've been assigned this slot before requesting to host !")

    def unassign_hosting_client(self, request):

        if request.slot_granted and request.host_granted:  # remove only if request's client already registered a slot and host
            # index of the requested slot in the self.list_slots
            idx_requested_slot = self.list_slots.index(request.slot)

            # modify the corresponding slot according to the request
            unassignment = self.list_slots[idx_requested_slot].unassign_hosting_client()

            if unassignment:
                # write the DB
                # home_db.unassign_hosting_client_db(request.slot.slot_id, db)
                pass
        else:
            raise ValueError("request.slot_granted OR request.host_granted is FALSE. The client has not been assigned"
                             "the slot OR hasn't been granted hosting.")

    def process_request(self, request):
        """
        Launch the logic processing of request
        :param request:
        :param app:
        :param id:
        :return:
        """
        """
        # thread for this submission => NOT USEFUL FOR SERVER IMPLEMENTATION
        threadObj_pending = threading.Thread(target=request.roadshow.logic, kwargs={'r': request,
                                                                                    'app': app,
                                                                                    'id_windows': id_windows,
                                                                                    'sub_window_id': sub_window_id,
                                                                                    'db': db
                                                                                    }
                                             )
        threadObj_pending.start()
        """
        # simple trigger
        return self.logic(r=request)

    def logic(self, r):
        """
        Function containing the first pass logic. (second pass, after pending is )Given a request:
            - assign client into slot,
            - ask to renew request (slot not available)
            - assign hosting,
            - set request as pending before confirmation,
        :param r: request instance
        :return: tuple of int, (book_slot, host_slot, duration)
            1: accepted
            0: rejected
            -1: pending
            ex: (1, 1, 0) accepted everywhere thus doesn't need to wait: duration of waiting is 0

            Some rules:
                if book_slot == -1:
                    host_slot, duration = 0, 0;


        """
        # Output initilization
        book_slot = 0
        host_slot = 0
        confirm   = 0

        #
        requested_slot = r.slot
        idx_requested_slot = self.get_idx_requested_slot(requested_slot)
        self.record_request(r)

        # Case where at least one client can join the slot
        if requested_slot.slot_status():
            # SLOT ASSIGNMENT
            if r.client.tier in [1, 2]:  # Tier 1,2: automatically granted
                # Authorization granted to access the slot AND assignment
                r.slot_granted = True

                book_slot = 1  # book slot accepted
                # TODO OUTPUT HERE: slot booked

            elif r.client.tier == 3:  # Tier 3: slot assignment pending
                # TODO TIME DELAY HERE
                # time.sleep(r.time_delay)
                book_slot, host_slot, cf = self.logic_second_pass(r=r)
                # TODO OUTPUT HERE
                confirm += cf

            else:
                raise ValueError('r.client.tier. Client requesting does not have a tier comprised between 1 and 3 ')

            # HOSTING PLACE ASSIGNMENT
            # current hosting client of the requested slot
            host_client = self.list_slots[idx_requested_slot].gethosting_client()

            if r.ask_hosting and r.slot_granted:
                # ------------------ case when a tier 1 is making a request + want to host
                if r.client.tier == 1:
                    # case when slot is empty OR no other tier 1 already registered
                    if host_client.tier == 0:
                        # Authorization granted to host and assignment according to client's request
                        r.host_granted = True

                        # TODO OUTPUT HERE
                        host_slot = 1

                    elif host_client.tier in [2, 3]:
                        # wanna join? part
                        # TODO OUTPUT HERE
                        confirm = self.confirmation_handling_popup(request=r)

                    elif host_client.tier == 1:  # clash with another tier1
                        # TODO => not available for hosting
                        confirm = self.confirmation_handling_popup(request=r)

                    else:
                        raise ValueError('r.host_client.tier. Host clients handled here are among 0, 1, 2 or 3 only')

                # ------------------ case when a tier 2 is making a request
                elif r.client.tier == 2:

                    # case when slot is hosted by a tier 3 (normally never happen) or empty
                    print("HOST CLIENT !!!!!!!!!!!!!    ", host_client.tier)
                    if host_client.tier == 0 or host_client.tier == 3:
                        # app.setMessage(title=id_windows, text="We'll get back to you in "+ str(r.time_delay)
                        # + " secondes...")
                        time.sleep(r.time_delay)  # penalty
                        r.already_delayed = True  # it is going into the second pass
                        book_slot, host_slot, cf = self.logic_second_pass(r=r)
                        confirm += cf

                    # case when slot is hosted by a tier 1
                    elif host_client.tier == 1:
                        # TODO OUTPUT HERE
                        confirm = self.confirmation_handling_popup(request=r)

                    # hosted by a tier 2
                    elif host_client.tier == 2:  # clash with other tier 2
                        # TODO OUTPUT HERE
                        confirm = self.confirmation_handling_popup(request=r)

                    else:
                        raise ValueError('r.host_client.tier. Host clients handled here are among 0, 1,2 or 3 only')

                # ------------------ case when a tier 3 is making a request to host
                elif r.client.tier == 3:
                    if host_client == 0:
                        pass
                    else:
                        # TODO OUTPUT HERE
                        confirm = self.confirmation_handling_popup(request=r)
                else:
                    raise ValueError('client.tier. Client requesting does not have a tier comprised between 1 and 3 ')

            elif not r.ask_hosting:
                if host_client.tier == 0:
                    # app.setMessage(title=id_windows, text="You successfully registered for this slot! \n"
                    #                                      "Nobody is hosting yet, we'll get back to you \n"
                    #                                      "as soon as a host is designated.")
                    # TODO OUTPUT HERE
                    book_slot = 1
                else:
                    confirm = self.confirmation_handling_popup(request=r)


        else:
            # app.setMessage(title=id_windows, text="This slot is full, please renew your request with another slot.")
            pass

        return book_slot, host_slot, confirm

    def logic_second_pass(self, r):
        """
        Second pass into the logic after pending time. Can only be called from self.logic_request()
        :param r:
        :param app
        :param id_windows
        :param db
        :return:
        """
        requested_slot = r.slot
        idx_requested_slot = self.get_idx_requested_slot(requested_slot)

        book_slot = 0
        host_slot = 0
        confirm   = 0

        if r.client.tier in [1, 2, 3]:  # useless...
            if not r.slot_granted and r.client.tier == 3:
                if r.slot.slot_status():
                    # Authorization granted to access the slot AND assignment
                    r.slot_granted = True
                    # TODO OUTPUT HERE: slot booked after waiting
                    book_slot = 1
                else:
                    # app.setMessage(title=id_windows,
                    #               text="This slot is not available, please renew your request with another slot.")
                    pass

            else:
                # current hosting client of the requested slot
                host_client = self.list_slots[idx_requested_slot].gethosting_client()

                if not r.host_granted and r.ask_hosting:  # client wants to host but hasn't been granted to
                    # ------------------ case when a tier 1 is making a request + want to host
                    if r.client.tier in [1, 2, 3]: # r.client.tier = 1 SHOULD NEVER HAPPEN
                        # case when slot is empty
                        if host_client.tier == 0:
                            # TODO: Pb if place already assigned => kicked out
                            # Authorization granted to host and assignment according to client's request
                            r.host_granted = True
                            # TODO OUTPUT HERE
                            host_slot = 1

                            if r.client.tier == 3:
                                # app.setMessage(title=id_windows, text="You successfully registered for this slot! \n "
                                #                          "You will host the event as well.\n"
                                #                                      "(this is a tier 3 hosting ???)")
                                pass
                            else:
                                # app.setMessage(title=id_windows, text="You successfully registered for this slot! \n "
                                #                           "You will host the event as well.\n")
                                pass

                        elif host_client.tier in [1, 2, 3]:
                            # TODO OUTPUT HERE
                            confirm = self.confirmation_handling_popup(request=r)

                        else:
                            raise ValueError('r.host_client.tier. Host clients handled here are among 1,2 or 3 only')
                    else:
                        raise ValueError(
                            'client.tier. Client requesting does not have a tier comprised between 1 and 3 ')

                else:
                    if host_client.tier == 0:
                        # app.setMessage(title=id_windows, text="You successfully registered for this slot! \n"
                        #                                      "Nobody is hosting yet, we'll get back to you \n"
                        #                                      "as soon as a host is designated.")
                        pass
                    else:
                        # TODO OUTPUT HERE
                        confirm = self.confirmation_handling_popup(request=r)

        else:
            raise ValueError('r.client not in [1, 2, 3]')

        return book_slot, host_slot, confirm

    def confirmation_handling_popup(self, request):
        """
        Handles the confirmation step, with pop up window and transaction handling
        :param request, Request object
        :return: int
        """
        return 1

########################################################################################################


class Request:
    def __init__(self, slot, client, ask_hosting, roadshow, time_of_request):
        """
        Bears the characteristics of a request

        :param slot: slot object
        :param client: client object
        :param ask_hosting: boolean, True or False
        :param time_of_request: datetime.datetime object
        :param roadshow, roadshow for which the request is made

        """
        # (subclass initialization)
        self.roadshow = roadshow

        if slot in self.roadshow.list_slots:
            self.slot = slot
        else:
            raise ValueError("slot. Choose among the existing slots please!")

        self.client = client
        self.ask_hosting = ask_hosting
        # TODO make sure this way of retrieving request time is fair for the system
        self.time_of_request = time_of_request  # keep track of request chronology for pending requests assignment

        # TODO shouldn't appear as parameters, but has to be set to False: For testing purpose
        self.slot_granted = False
        self.host_granted = False

        # allow background operation by assigning one thread per request
        if self.client.tier == 1:
            self.time_delay = 0
        elif self.client.tier == 2:
            self.time_delay = 15  # 5s delay for tier 2 clients
        elif self.client.tier == 3:
            self.time_delay = 20
        elif self.client.tier not in [1, 2, 3]:
            raise ValueError('self.client.tier. should be 2 or 3 only, here it is '+str(self.client.tier))

        # Request already delayed?
        self.already_delayed = False

    """ ------- Allows respectively: == comparison, != comparison, set making, len() function among others---------"""
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

    """------------------------------------------------------------------------------------------------------------"""

########################################################################################################
def main(asking_client, slot_id, willing_to_host):
    """
    Run the logic given all the elements making a request.
    """

    # Objects creation from database
    config_name = os.getenv('FLASK_CONFIG')

    # Clients Roadshows and Slots
    _, app, _ = create_app(config_name=config_name)  # global db object to query the db
    with app.app_context():
        # Clients
        clients = Clients.query.all()
        list_clients = [Client(client_id=client.client_id,
                               tier=client.tier,
                               location=client.location,
                               name=client.client_name)
                        for client in clients]

        # Roadshow and slots
        roadshows = Roadshows.query.all()
        list_roadshows = []
        for roadshow in roadshows:
            # Slots for each roadshow
            # hosting clients
            slots = Slots.query.filter(Slots.roadshow == roadshow.roadshow_id).all()
            # print("SLOTS: ", [cl for cl in list_clients if cl.client_id == slots[0].hosting_client][0])
            list_slots = [Slot(start_time=slot.date_time,
                               slot_id=slot.slot_id,
                               hosting_client=
                               [cl if cl.client_id == slot.hosting_client else None for cl in list_clients][0],
                               max_client=slot.max_nb_clients,
                               slotname=slot.slot_name)
                          for slot in slots]

            list_roadshows.append(Roadshow(
                roadshow_id=roadshow.roadshow_id,
                list_slots=list_slots,
                roadshow_name=roadshow.roadshow_name
            )
            )
            current_client = [cl for cl in list_clients if cl.client_id == asking_client][0]
            current_roadshow = [rd for rd in list_roadshows for sl in rd.list_slots if sl.slot_id == slot_id][0]
            current_slot = [sl for sl in current_roadshow.list_slots if sl.slot_id == slot_id][0]

    # Request
    request = Request(slot=current_slot,
                      client=current_client,
                      ask_hosting=willing_to_host,
                      roadshow=current_roadshow,
                      time_of_request=datetime.datetime.now()
                      )

    # Process Request and get output
    current_roadshow.process_request(request=request)



