import serial
from xbee import XBee, ZigBee
import time
import json

serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.
print(xbee)
#destAddress = '0013A20041574921'
#destAddress = destAddress.lower()
#print(destAddress)
#destAddress = destAddress.decode('hex')

#print(destAddress)

xbee.open()

# Get the network.
xnet = xbee.get_network()
print(xnet)

while True:
    try:
        time.sleep(10)
        print('sending at command')
        A = xbee.remote_at(dest_addr_long="\x00\x13\xa2\x00AWI!",command="P1",parameter='\x05') #\x05 means digital high, or True, or LED off (for this pin)
        #xbee.remote_at(destAddress,command="P1",parameter='\x05') #\x05 means digital high, or True, or LED off (for this pin)
        print(A)
        response = xbee.wait_read_frame()
        print(response)
    except KeyboardInterrupt:
    
        break

serial_port.close()