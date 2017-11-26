# created 9-10-17

import os

import sys
sys.path.append(".")
from app import create_app

""""

"""
# TODO in this project
# implement a background running task for client's requests pending approval.
#   -> should use Celery http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html I think


config_name = os.getenv('FLASK_CONFIG')
manager, app, migrate = create_app(config_name)

if __name__ == '__main__':
    manager.run()
