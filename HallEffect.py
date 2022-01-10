import RPi.GPIO as GPIO
from time import sleep, strftime, time  # strtime & time only for file output
import time, math
import os  # needed to find out if output directory already exists
from datetime import datetime  # needed to add time and date to output file

gpio_pin_number = 5  # GPIO Pin used by sensor
wheel_diameter_in = 20  # wheel diameter in inches
adjustment = 1  # adjustment for gear ratio or number of magnets
seconds = 1  # time to wait between printing values
rpm = 0
mph = 0
prev_mph = 0
accel = 0
elapsed_time = 0  # amount of time a full revolution takes
number_interrupts = 0  # counts interrupts (triggered by sensor)
previous_number_interrupts = 0
start_timer = time.time()

parent_dir = "/home/pi/Desktop/"  # parent directory path
directory = "Sensor_logs/"  # new directory name - slash at end is important
file_name = "RPM_logs_"  # file name prefix for log file

path = os.path.join(parent_dir, directory)  # full path to log file

# print (f"path= {path}")   # use to check directory path

try:  # create directory if it doesn't exist, tell us if it already does
    os.mkdir(path)
    print("Directory '% s' created" % directory)
except FileExistsError:
    print("folder already exists")

filename = file_name + str(datetime.now().strftime('%Y_%m_%d_%H%M%S')) + '.csv'
filepath = str(path + filename)


# print(filepath)   # uncomment to check file path

def init_GPIO():  # initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(gpio_pin_number, GPIO.IN, GPIO.PUD_UP)


def calculate_elapsed_time(channel):
    global number_interrupts, start_timer, elapsed_time, signal
    number_interrupts += 1  # increase by 1 whenever an interrupt occurs
    elapsed_time = time.time() - start_timer  # time each rotation takes
    start_timer = time.time()  # Set start_time to current time


def calculate_speed(wheel_diameter):
    global number_interrupts, elapsed_time, rpm, mph, prev_mph
    if elapsed_time != 0:  # avoid DivisionByZero error
        rpm = (1 / elapsed_time * 60) * adjustment
        wheel_circumf_in = math.pi * wheel_diameter  # wheel circumference in inches
        prev_mph = mph
        mph = (rpm * wheel_circumf_in) / 1056

def calculate_accel():
    global number_interrupts, elapsed_time, mph, prev_mph, accel
    if elapsed_time != 0:  # avoid DivisionByZero error
        accel = (mph - prev_mph) / elapsed_time * 0.44704


def init_interrupt():
    GPIO.add_event_detect(gpio_pin_number, GPIO.FALLING, callback=calculate_elapsed_time, bouncetime=20)


if __name__ == '__main__':
    init_GPIO()
    init_interrupt()
    with open(filepath, "a") as log:
        while True:

            if number_interrupts != previous_number_interrupts:
                calculate_speed(wheel_diameter_in)  # call this function with wheel diameter as parameter
                print(f"RPM = {round(rpm)}, MPH = {round(mph, 1)}")
                log.write("{0},{1},{2}\n".format(str(round(rpm)), (str(round(mph, 1))),
                                                strftime("%Y-%m-%d %H:%M:%S")))  # write RPM and time to log file

            if (number_interrupts == previous_number_interrupts):  # no new interrupts, so rpm & mph = 0
                rpm = 0
                mph = 0.0
                print(f"RPM = {round(rpm)}, MPH = {round(mph, 1)}")
                log.write(
                    "{0},{1}\n".format(str(round(rpm)), strftime("%Y-%m-%d %H:%M:%S")))  # write RPM and time to log file

            previous_number_interrupts = number_interrupts

            sleep(seconds)  # wait before displaying & writing more data
