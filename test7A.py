#This script does the same thing as test6.py, but it connects to our own instance of thingsboard, not the test version provided by thingsboard ( "demo.thingsboard.io" )


import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
from random import *


#mqttBroker = "demo.thingsboard.io"
mqttBroker = "192.155.83.191"
mqttClientId     = "ewanderson"
mqttUserName     = "A3QMO5nbq9QnJ53A5w2k" #this is an access token that will direct my data to a specific device on thingsboard 

topic = "v1/devices/me/attributes" #This is the topic for attributes in thingsboard  
addr_extended = "\x00\x13\xa2\x00A'\xca\xe8"
addr = "\xff\xfe"
rpcTopic = "v1/devices/me/rpc/request/+"
topicTelem = "v1/devices/me/telemetry"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.subscribe(rpcTopic)

    


# The callback for when an RPC message is received from the server.
def on_message(client, userdata, msg):
    print 'Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload)
    # Decode JSON request
    data = json.loads(msg.payload)
    # Check request method
    if data['params']:
    	xbee.remote_at(dest_addr_long="\x00\x13\xa2\x00A'\xca\xe8",command="D4",parameter='\x04') #\x04 means digital low, or False, or LED on (for this pin)
    else: #if switchStatus is set to false
 		xbee.remote_at(dest_addr_long="\x00\x13\xa2\x00A'\xca\xe8",command="D4",parameter='\x05') #\x05 means digital high, or True, or LED off (for this pin)





MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

MQTT.loop_start()


serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.

while True:
    try:

        response = xbee.wait_read_frame() #Wait for an API frame to arrive. Note: this blocks while it is waiting.
        IO_Data = response.get('samples')[0] #The .get() outputs a 1 element long list, where the element is a dict. Adding the [0] stores the dict in IO_Data instead of the list containing the dict.

        #Publish pin 3 & 4 status to thingsboard over MQTT 
        message = str(IO_Data) #Convert IO_Data to a string (format required by publish).
        #print response
        print message
        MQTT.publish(topic, message, qos=1, retain=False)
        
        Power = randint(80, 100) #We're not actually measuring power at this point, so I'm going to generate a random number and pretent it's the production.
        messageTelem = "{'Power': "+str(Power)+"}"
        print(messageTelem)
        print(topicTelem)
        print(MQTT.publish(topicTelem, messageTelem, qos=1, retain=False))
        

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 
