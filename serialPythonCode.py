#!/usr/bin/env python3
import serial
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            exit()
# run in termial as "sudo python3 serialPythonCode.py > output.txt" 
# make sure rx of esp32 is connected to tx0 of rasp pi and vice versa
# the esp32 and the raspberry pi should be grounded together 
            