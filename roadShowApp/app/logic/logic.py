from ..models import Roadshows, Requests, Slots, Clients, Attendance
from .. import create_app
import os

config_name = os.getenv('FLASK_CONFIG')
_, app, _ = create_app(config_name=config_name)  # global db object to query the db


def logic_draft(client_id, willing_to_host, hosting_client):
    """
    :param willing_to_host, int: means actually willing_to_host when Nobody is hosting but means confirmation
    when somebody is hosting
    :param client_id, int
    :param hosting_client, int

    :return: tuple (book_slot: int, host_slot: int, delayed: int):
    if delayed == 0
        book_slot = 1 => slot successfully booked
        book_slot = 0 => slot unsuccessfully booked

        host_slot = 1 => slot will be hosted
        host_slot = 0 => slot unsuccessfully hosted

    if delayed == 1
        book_slot = 1 AND host_slot = 1 => booking of slot delayed (tier 3 for instance)
        book_slot = 1 AND host_slot = 0 => hosting is delayed (tier 2 and 3 for instance)
    """
    book_slot = 0
    host_slot = 0
    delayed = 0

    with app.app_context():
        client = Clients.query.filter_by(client_id=client_id).first()

    if willing_to_host == 1 and hosting_client != 0:
        # wanna join
        if client.tier == 1:
            # book slot
            book_slot += 1
        elif client.tier == 2:
            # book slot
            book_slot += 1

        elif client.tier == 3:
            # delay
            delayed += 1
            book_slot += 1
            host_slot += 1

        else:
            raise ValueError("app/request/views.py: Tier should be comprised btw 1 and 3.")

    elif willing_to_host == 1 and hosting_client == 0:
        # wanna host
        if client.tier == 1:
            # book and host slot
            book_slot += 1
            host_slot += 1

        elif client.tier == 2:
            # book slot delayed host
            delayed += 1
            # no change to book_slot
            host_slot += 1

        elif client.tier == 3:
            # delay
            delayed += 1
            book_slot += 1
            host_slot += 1
        else:
            raise ValueError("app/request/views.py: Tier should be comprised btw 1 and 3.")

    elif willing_to_host == -1 and hosting_client == 0:
        # don't wanna host
        if client.tier == 1:
            # book and host slot
            book_slot += 1

        elif client.tier == 2:
            # book slot delayed host
            book_slot += 1

        elif client.tier == 3:
            # delay
            delayed += 1
            book_slot += 1
            host_slot += 1

        else:
            raise ValueError("app/request/views.py: Tier should be comprised btw 1 and 3.")

    return book_slot, host_slot, delayed
