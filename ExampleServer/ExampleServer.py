# ExampleServer.py

"""
Run this application by:
    Make sure you cd into this directory: ExampleServer/
    1) Creating a venv (virtual environment)
        - I like to use venv's to manage packages for a python project
        - to create a venv, run:
            python -m venv venv
        - this will create a new venv in the directory "./venv"
    2) activating the venv (virtual environment, which contains the
       packages needed)
        - $ . venv/bin/activate
        - When you do this, you should see (venv) at the start of your
        command line
    3) Install the needed packages to the venv
        - $ pip install -r requirements.txt
    4) Run the python script
        - $ python ExampleServer.py
"""

# I think there's a way to configure virtual environments with pycharm
# so you can just hit the green arrow to run, so if people don't want
# to use the command line we can figure that out too

from datetime import datetime
from flask import Flask, render_template, jsonify
from threading import Thread
import time
import signal

# DATA-UPDATING THREAD(S) ##############################################


# Just for ease of testing, so only one interrupt is needed to stop the
# server and thread
def handle_keyboard_int(signal, stack_frame):
    global incrementing
    incrementing = False
    raise KeyboardInterrupt()


# Link handle_keyboard_int function to a SIGINT signal (ctrl-c)
signal.signal(signal.SIGINT, handle_keyboard_int)


def increment_var():
    global counter
    while incrementing:
        counter = counter + 1
        time.sleep(1)


# Create a global variable and a thread for incrementing it
# When transferring this same kinda logic over to the data from the
# sensors, we would probably just do the same thing but with global
# variables for each of the sensor data values
counter = 0
incrementing = True
t = Thread(target=increment_var)

########################################################################


# FLASK SERVER #########################################################

# Creates a flask app (which is just an instance of the Flask class)
app = Flask(__name__)


# Create a basic route for the flask server
@app.route("/")
def index():
    # Renders the index.html template (in the templates folder)
    return render_template("index.html", counter=counter)


# route to return current value of my_variable
@app.route("/update", methods=["POST"])
def update():
    return jsonify(
        {"value": counter, "time": datetime.now().strftime("%H:%M:%S")}
    )

########################################################################

# Can also run the application with the following command line commands
# $ export FLASK_APP=SimpleServer
# $ python -m flask run

# For continuously updating the page
# https://stackoverflow.com/questions/59780007/ajax-with-flask-for-real-time-esque-updates-of-sensor-data-on-webpage


if __name__ == "__main__":
    t.start()
    app.run(debug=True)
