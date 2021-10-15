"""
Run this application by:
    Make sure you cd into this directory: ExampleServer/
    1) activating the venv (virtual environment, which contains the
       packages needed)
        - $ . venv/bin/activate
        - When you do this, you should see (venv) at the start of your
        command line
    2) Install the needed packages
        - $ pip install -r requirements.txt
    3) Run the python script
        - $ python SimpleServer.py
"""

# I think there's a way to configure virtual environments with pycharm
# so you can just hit the green arrow to run, so if people don't want
# to use the command line we can figure that out too

from flask import Flask, render_template

# Creates a flask app (which is just an instance of the Flask class)
app = Flask(__name__)


# Create a basic route for the flask server
@app.route("/")
def index():
    # Renders the index.html template (in the templates folder)
    return render_template("index.html")


# Can also run the application with the following command line commands
# $ export FLASK_APP=SimpleServer
# $ python -m flask run


if __name__ == "__main__":
    app.run(debug=True)
