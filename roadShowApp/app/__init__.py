# __init__.py created on 9-10-17
# Equivalent of /Users/Louis/PycharmProjects/covalent_capital/Roadshow_planner/cloud_deployment/getting-started-python/2-structured-data/bookshelf/model_cloudsql.py
# third-party imports
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_bootstrap import Bootstrap

import sys
sys.path.append("..")

"""
We've created a function, create_app that, given a configuration name,
loads the correct configuration from the config.py file,
as well as the configurations from the instance/config.py file.
We have also created a db object which we will use to interact with the database.
"""

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()

# after the db variable initialization
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    # TODO change this path
    app.config.root_path = "/Users/Louis/PycharmProjects/covalent_capital/Roadshow_planner/roadShowApp/"
    app.config.from_pyfile('instance/config.py')
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"   

    # migration object
    migrate = Migrate(app, db)

    # boostrap
    Bootstrap(app)

    from app import models

    # TODO Do not forget to register new blueprints when adding functionalities to your app /!\
    # register blueprints
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from app.request import request as request_blueprint
    app.register_blueprint(request_blueprint)

    # Wrap everything in a manager
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500

    @app.route('/500')
    def error():
        abort(500)

    return manager, app, migrate
