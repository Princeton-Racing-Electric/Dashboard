# Server.py

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
from doctest import Example
from flask import Flask, render_template, jsonify
from threading import Thread
#from playsound import playsound
import time, math
import signal
import sys
import os
import can
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import HallEffect
import Voltage
import webbrowser # open a webbrowser
from Temperature import read_temp 

# Constants
DELAY_TIME = 1
WHEEL_DIAMETER_IN = 20
nodeID = 1

# GLOBAL VARIABLES 
# for sensor data
mph = 0
accel = 0
temperature = 0
voltage = 0
miles = 0
# for threading
counter = 0
running = True

# for can
can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes') #might need to change to pcan

# Just for ease of testing, so only one interrupt is needed to stop the
# server and thread
def handle_keyboard_int(signal, stack_frame):
    global running
    running = False
    raise KeyboardInterrupt()

def can_init():
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

# Link handle_keyboard_int function to a SIGINT signal (ctrl-c)
signal.signal(signal.SIGINT, handle_keyboard_int)

#import webbrowser, os, sys
#url = "http://127.0.0.1:5000/"
#chrome_path = '/usr/lib/chromium-browser/chromium-browser'
#webbrowser.get(chrome_path).open(url)

# MAYBE: we could make a sensors class that encapsulates all the needed
# code for the sensors, then we can just create an instance of that here
# it could have get_speed and get_temp...
# Data-fetching functions for sensors #######
# returns the current speed in miles per hour using the hall effect
# sensor
def get_speed() -> float:
    #num_interrupts = HallEffect.number_interrupts
    #prev_num_interrupts = HallEffect.previous_number_interrupts
    #mph = 0

    #if num_interrupts != prev_num_interrupts:
    #    HallEffect.calculate_speed(WHEEL_DIAMETER_IN)
    #    mph = HallEffect.mph
    msgS = can.Message(arbitration_id=0x600 + nodeID, data=[0x40, 0x6C, 0x60, 0x00, 0x00, 0x00, 0x00], extended_id=False)
    can0.send(msgS)
    msgR = can0.recv(30.0)
    mph = int(msgR.data[3], 16) + (2**8)*int(msgR.data[2], 16) + (2**16)*int(msgR.data[1], 16) + (2**24)*int(msgR.data[0], 16)
    print(mph)
    return mph

def get_accel() -> float:
    num_interrupts = HallEffect.number_interrupts
    prev_num_interrupts = HallEffect.previous_number_interrupts
    accel = 0

    if num_interrupts != prev_num_interrupts:
        HallEffect.calculate_accel()
        accel = HallEffect.accel

    return accel

# returns the current temperature in (???) from the temp sensor
def get_temp() -> float:
    return read_temp()[0]

def get_volt() -> float:
    ad_value = Voltage.readadc(Voltage.AO_pin, Voltage.SPICLK, Voltage.SPIMOSI, Voltage.SPIMISO, Voltage.SPICS)
    return ((ad_value * (3.3 / 1024) * 5) / 12) * 100

def get_miles() -> float:
    miles = HallEffect.number_interrupts * WHEEL_DIAMETER_IN * math.pi / 63360
    return miles
############################################


# Data-updating functions for threads #######
# Update speed
def update_speed():
    global mph
    while running:
        mph = get_speed()
        time.sleep(DELAY_TIME)

def update_accel():
    global accel
    while running:
        accel = get_accel()
        time.sleep(DELAY_TIME)


# Update temperature
def update_temp():
    global temperature
    while running:
        temperature = get_temp()
        time.sleep(DELAY_TIME)

# Update voltage
def update_volt():
    global voltage
    while running:
        voltage = get_volt()
        time.sleep(DELAY_TIME)

# Update miles
def update_miles():
    global miles
    while running:
        miles = get_miles()
        time.sleep(DELAY_TIME)


# Update test variable
def increment_var():
    global counter
    while running:
        counter = counter + 1
        time.sleep(DELAY_TIME)

######################################################
# function to play sound  -- need to set variables, find wav files, and temperature/battery limits
def playSound(voltage, temperature):
    if (voltage > 1): 
        wavFile = input("Enter a wav filename:")
        playsound(wavFile)
    if (temperature > 1):
        wavFile = input("Enter a wav filename:")
        playsound(wavFile)

##############################


# Create a global variable and a thread for updating it
# When transferring this same kinda logic over to the data from the
# sensors, we would probably just do the same thing but with global
# variables for each of the sensor data values

running = True
t1 = Thread(target=increment_var)
# could maybe combine the sensors into just one thread?
t2 = Thread(target=update_speed)
t3 = Thread(target=update_temp)
t4 = Thread(target=update_volt)
t5 = Thread(target=update_miles)
t6 = Thread(target=update_accel)

##############################################################

# FLASK SERVER #########################################################
# Creates a flask app (which is just an instance of the Flask class)
app = Flask(__name__)


# Create a basic route for the flask server
@app.route("/")
def index():
    # Renders the index.html template (in the templates folder) - must match the html file 
    return render_template("boardv2.html", counter=counter)

# route to return current value of my_variable
@app.route("/update", methods=["POST"])
def update():
    return jsonify(
        {
            "value": counter,
            "mph": mph,
            "acceleration": accel,
            "temperature": temperature,
            "voltage": voltage,
            "mileage": miles,
            "time": datetime.now().strftime("%H:%M:%S")
        }
    )
########################################################################
# Test code to ensure that button goes to app.route on click
@app.route('/test')
def test():
    print ('I got clicked\n')
    return 'Clicked'

########################################################################

# restarts the raspberry pi
# runs the bash script sudo shutdown -r now
@app.route("/restart")
def restart():
    os.system("sudo reboot")

def restart2():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    subprocess.run("shutdown -h 0", shell=True, check=True)
    print(output)

########################################################################

# Can also run the application with the following command line commands
# $ export FLASK_APP=SimpleServer
# $ python -m flask run

# For continuously updating the page
# https://stackoverflow.com/questions/59780007/ajax-with-flask-for-real-time-esque-updates-of-sensor-data-on-webpage


if __name__ == "__main__":
    HallEffect.init_GPIO()
    HallEffect.init_interrupt()
    Voltage.init()
    can.init()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    app.run(debug=True)
    # app.run(host='127.0.0.1', port = 5000, debug=True)  
    #command = "chromium-browser https://127.0.0.1:5000"
    #import subprocess
    #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    #output = process.communicate()[0]
    #print(output)
