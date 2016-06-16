#!python3
import serial
import sys
import time

baud = 9600
port = sys.argv[1]
msg = sys.argv[2]

ser = serial.Serial(port, baud, timeout=10)
time.sleep(2)
ser.write(msg.encode("ascii"))
ser.close()
