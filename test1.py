#This script waits for API frames from remote XBees then prints the pin status portions of the API frame to screen.

import serial
from xbee import XBee, ZigBee


serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.

while True:
    try:

        response = xbee.wait_read_frame() #Wait for an API frame to arrive. Note: this blocks while it is waiting.

        IO_Data = response.get('samples')[0] #The .get() outputs a 1 element long list, where the element is a dict. Adding the [0] stores the dict in IO_Data instead of the list containing the dict.
        print IO_Data #Print all configured pins and statuses
        print IO_Data.get('dio-4') #print just, pin 4 status

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 
