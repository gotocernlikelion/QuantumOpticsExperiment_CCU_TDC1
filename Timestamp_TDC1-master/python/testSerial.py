
import serial
import time

from serial import SerialException


ser = serial.Serial('COM3')  # open serial port
print(ser.name)         # check which port was really used
ser.write(('MODE?;' + '\n').encode())
time.sleep(1)
Buffer_length = ser.in_waiting
print(str(Buffer_length) + " Bytes Recorded")
print (ser.read(Buffer_length))


##### If you see the device responding 0 (single), 1 (pair), or 3 (timestamp) , you are

