# Instructions for enabling the temperature sensor:
# 1. At the command prompt, enter sudo nano /boot/config.txt, then add this to the bottom of the file:
# dtoverlay=w1-gpio
# 2. Exit Nano, and reboot the Pi with sudo reboot
# 3. Log in to the Pi again, and at the command prompt enter sudo modprobe w1-gpio
# 4. Then enter sudo modprobe w1-therm
# 5. Change directories to the /sys/bus/w1/devices directory by entering cd /sys/bus/w1/devices
# 6. Now enter ls to list the devices:
# In my case, 28-000006637696 w1_bus_master1 is displayed.
# 7. Now enter cd 28-XXXXXXXXXXXX (change the X’s to your own address)
# For example, in my case I would enter cd 28-000006637696
# 8. Enter cat w1_slave which will show the raw temperature reading output by the sensor:
# Here the temperature reading is t=28625, which means a temperature of 28.625 degrees Celsius.
# 9. Enter cd to return to the root directory
# That’s all that’s required to set up the one wire interface.

import glob
from time import sleep, strftime, time  # strtime & time only for file output
import time, math
import os  # needed to find out if output directory already exists
from datetime import datetime  # needed to add time and date to output file

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


while True:
    print(read_temp())
    time.sleep(1)
