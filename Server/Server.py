# Server.py

from datetime import datetime
from doctest import Example
from flask import Flask, render_template, jsonify
from threading import Thread, Timer
from playsound import playsound
import time, math
from time import gmtime, strftim
import signal
import serial
import sys
import os
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


# Just for ease of testing, so only one interrupt is needed to stop the
# server and thread
def handle_keyboard_int(signal, stack_frame):
    global running
    running = False
    raise KeyboardInterrupt()


# Link handle_keyboard_int function to a SIGINT signal (ctrl-c)
signal.signal(signal.SIGINT, handle_keyboard_int)

# MAYBE: we could make a sensors class that encapsulates all the needed
# code for the sensors, then we can just create an instance of that here
# it could have get_speed and get_temp...
# Data-fetching functions for sensors #######
# returns the current speed in miles per hour using the hall effect
# sensor

def get_speed() -> float:
    #if ser.in_waiting > 0:
    line = ser.readline().decode('utf-8').rstrip()
    return float(line)

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
        #mph = 5
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
        print(miles)
        time.sleep(DELAY_TIME)

# Update count variable
def increment_var():
    global counter
    while running:
        counter = counter + 1
        time.sleep(DELAY_TIME)
        

######################################################
# function to play sound  -- need to set variables, find wav files, and temperature/battery limits
def playSoundVolt():
    print(voltage)
    if (voltage < 20): # under 20%
        #wavFile = input("Enter a wav filename:")
        #playsound(r'/home/pi/Desktop/Dashboard/Server/voltage_alert.wav')
        os.system('omxplayer /home/pi/Desktop/Dashboard/Server/voltage_alert.wav')
        print("playing voltage sound w/ .wav")
    #Timer(5, playSoundVolt).start()


def playSoundTemp():
    if (temperature > 80):
        #playsound(r'/home/pi/Desktop/Dashboard/Server/temperature_alert.wav')
        os.system('/home/pi/Desktop/Dashboard/Server/temperature_alert.wav')
        print("playing temperature sound w. .wav")
   # Timer(60, playSoundTemp).start()

##############################
# Create a global variable and a thread for updating it
# When transferring this same kinda logic over to the data from the
# sensors, we would probably just do the same thing but with global
# variables for each of the sensor data values

running = True
t1 = Thread(target=increment_var)
t2 = Thread(target=update_speed)
t3 = Thread(target=update_temp)
t4 = Thread(target=update_volt)
t5 = Thread(target=update_miles)
t6 = Thread(target=update_accel)



##############################################################

# FLASK SERVER
# Creates a flask app (which is just an instance of the Flask class)

app = Flask(__name__)

# Create a basic route for the flask server
@app.route("/")
def index():
    # Renders the index.html template (in the templates folder) - must match the html file 
    return render_template("boardv3.html", counter=counter)

# route to return current value of my_variable
@app.route("/update", methods=["POST"])
def update():
    if(counter % 10 == 0){
        printVariables()
        printVariablesToFile()
    }
    return jsonify(
        {
            "value": counter,
            "mph": mph,
            "acceleration": accel,
            "temperature": temperature,
            "voltage": voltage,
            "mileage": miles,
        }
    )

# Print all variables for debugging
def printVariables():
    print("Value:", counter)
    print("Velocity:", mph)
    print("Acceleration", accel)
    print("Temperature:", temperature)
    print("Voltage:", voltage)
    print("Mileage:", miles)
    
# Print all variables to file for logging
def printVariablesToFile():
    fileOut.write("Value: %d\n", counter)
    fileOut.write("Velocity: %d\n", mph)
    fileOut.write("Acceleration: %d\n", accel)
    fileOut.write("Temperature: %d\n", temperature)
    fileOut.write("Voltage: %d\n", voltage)
    fileOut.write("Mileage: %d\n", miles)

########################################################################

# restarts the raspberry pi
# runs the bash script sudo shutdown -r now
@app.route("/restart")
def restart():
    fileOut.close()
    os.system("sudo reboot")

def restart2():
    fileOut.close()
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    subprocess.run("shutdown -h 0", shell=True, check=True)
    print(output)

########################################################################

# Run the application:

if __name__ == "__main__":
    HallEffect.init_GPIO()
    HallEffect.init_interrupt()
    Voltage.init()
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.reset_input_buffer()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    
    actual_time = strftime("%Y-%m-%d %H-%M-%S", gmtime())

    global fileOut = open("DashboardLog - " + str(actual_time) + ".txt", "w")
    
    app.run(debug=True)

