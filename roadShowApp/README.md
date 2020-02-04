
## ROADSHOW PLANNER

Run the app:
- clone the repo
- create an environment which has all the requirements found in roadShowApp/requirements.txt
- you must have a MySQL client on the computer, accessible through command line or other (ex: SequelPro on Mac OSX)
- create a database and configure the file roadShowApp/instance/config.py with credentials and others (see comments)
- Go to the root directory, activate the environment and initialize the following variables (this has to be done
every time you close your terminal/shell)

        export FLASK_CONFIG=development
        export FLASK_APP=run.py
        export FLASK_DEBUG=1 (so that any change in the code automatically reloads the app without running "flask run")

- open your browser at http://127.0.0.1:5000 (normally port 5000)

# How does it work? #

Just follow the extremly clear tutorials here (three parts), from which this platform has been adapted
    https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-one

# Remarks #

- There are many TODO in this whole project. Taking time to review them could give an idea of what to do next, but also
what are some possible source of errors, like paths that must be changed first

- Quick word on Jinja syntax that allows to use python inside HTML:
    {%  instruction %}
        ex: {% if %}
                <p> html here </p>
            {% else %}
                <p> other html </p>
            {% endif %}

    {{ variable_value }}
        ex: <p> This is variable's value: {{ variable }} </p>

# Questions? #

louis.douge@gmail.com
