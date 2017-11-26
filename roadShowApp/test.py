# tests.py

import unittest

from flask_testing import TestCase

from .app import create_app, db
from .app.models import User
from .instance import config as conf_db


class TestBase(TestCase):

    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI=(
                'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{database}').format(
                user=conf_db.CLOUDSQL_USER, password=conf_db.CLOUDSQL_PASSWORD,
                database=conf_db.CLOUDSQL_DATABASE)
        )
        return app

    def setUp(self):
        """
        Will be called before every test
        """

        db.create_all()

        # create test admin user
        admin = User(email="test@test.com",
                     client_id=22,
                     password="admin2016",
                     first_name="test",
                     last_name="Test",
                     is_admin=True)

        # create test non-admin user
        employee = User(username="test_user", password="test2016")

        # save users to database
        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """

        db.session.remove()
        db.drop_all()

if __name__ == '__main__':
    unittest.main()