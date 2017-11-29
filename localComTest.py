#! /usr/bin/python
 
# Demo to talk to an XBee ZigBee device
# Per Magnusson, 2015-07-28
  
from xbee import XBee
import serial
import serial.tools.list_ports
import time
import sys
 
# Look for COM port that might have an XBee connected
# portfound = False
# ports = list(serial.tools.list_ports.comports())
# print(ports)
# for p in ports:
#     # The SparkFun XBee Explorer USB board uses an FTDI chip as USB interface
#     if "/dev/tty" in p[2]:
#         print( "Found possible XBee on " + p[0])
#         if not portfound:
#             portfound = True
#             portname = p[0]
#             print( "Using " + p[0] + " as XBee COM port.")
#         else:
#             print("Ignoring this port, using the first one that was found.")
#  
# if portfound:
#     ser = serial.Serial(portname, 9600)
# else:
#     sys.exit("No serial port seems to have an XBee connected.")
 
ser = serial.Serial('/dev/tty.usbserial-A505NAFC', 9600)
 
# Flash the LED attached to DIO1 of the XBee
try:
    print(0)
    xbee = XBee(ser)
    print("XBee test")
 
    xbee.at(command='D4', parameter='\x04') # Pin 1 low
    print(1)
    print(xbee.wait_read_frame())
    resp = xbee.wait_read_frame()
    print(2)
    print(resp)
    print(3)
 
    time.sleep(1)
    xbee.at(command='D4', parameter='\x05') # Pin 1 high
    print(4)
    resp = xbee.wait_read_frame()
    print(resp)
 
    # Try another AT command
    xbee.at(command='ID')
    resp = xbee.wait_read_frame()
    print(resp)
    print("Done")
    ser.close()
except:
    print("Error!")
    ser.close()
 
#raw_input("Press Enter to continue...")