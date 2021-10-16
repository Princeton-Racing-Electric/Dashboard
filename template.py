#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#       Hall Effect Sensor
#
# This script tests the sensor on GPIO17.
#
# Author : Matt Hawkins
# Date   : 08/05/2018
#
# https://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

# Import required libraries
import time
import math
import datetime
import RPi.GPIO as GPIO
# Temporary values:
hall_pin = 7
circ = 8 * math.pi # Wheel circumference in
def hallSensing(channel):
  # Called if sensor output changes
  global RPM, speed, this_time, last_time
  this_time = time.time()
  RPM = (1/(this_time - last_time))*60
  speed = RPM * circ * 60 / (12*5280) # Converting from RPM to mph
  last_time = this_time

def main():
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  # Get initial reading
  hallSensing(hall_pin)

  try:
    # Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

print("Setup GPIO pin as input on GPIO17")

# Set Switch GPIO as input
# Pull high by default
GPIO.setup(hall_pin , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(hall_pin, GPIO.RISING, callback=hallSensing, bouncetime=1)

if __name__=="__main__":
   main()