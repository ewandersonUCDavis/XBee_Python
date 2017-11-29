#This extends test2.py. In addition to sending pin status to MQTT server this script subscribes to the status of the shared attribute "Switch". When Switch is changed in thingsboard the dio-4 pin on the remote XBee is updated to match the value of "Switch". I'm also changing pin statuses from telemetry to attributes. This script demonstrates three new abilities (compared to test2.py): 1) This script simultaneously listens to both the XBee network (blocking) and the MQTT server (non blocking). 2) this script remotely set's a dio pin value using remote_at() 3) this script receives messages (about shared attribute updates) from the mqtt server. 

import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json

mqttBroker = "demo.thingsboard.io"
mqttClientId     = "ewanderson"
mqttUserName     = "HgQrDJl1F8Hgr1BpfT54" #this is an access token that will direct my data to a specific device on thingsboard HgQrDJl1F8Hgr1BpfT54

topic = "v1/devices/me/attributes" #This is the topic for attributes in thingsboard  
addr_extended = "\x00\x13\xa2\x00A'\xca\xe8"
addr = "\xff\xfe"





# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    MQTT.subscribe(topic,qos=1) #This subscribes to changes in shared attributes, but not changes in client attributes.






# The callback for when a PUBLISH message is received from the server.
def on_message(MQTT, userdata, msg):
	print("subscription message recieved.")
	print(msg.topic+" "+str(msg.payload))
	jsonPayload = json.loads(msg.payload) #The message is received as a string. This line converts it to a dict so parameter values can be extracted using key words.
	switchStatus = jsonPayload['Switch']  #This line extracts the value of the parameter 'Switch' (switchStatus is a bool)
	#type(switchStatus)
	if switchStatus: #if switchStatus is set to true
		xbee.remote_at(dest_addr_long="\x00\x13\xa2\x00A'\xca\xe8",command="D4",parameter='\x05') #\x05 means digital high, or True
	else: #if switchStatus is set to false
		xbee.remote_at(dest_addr_long="\x00\x13\xa2\x00A'\xca\xe8",command="D4",parameter='\x04') #\x04 means digital low, or False




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

        #Publish pin 4 status to thingsboard over MQTT 
        message = str(IO_Data) #Convert IO_Data to a string (format required by publish).
        #print response
        print message
        MQTT.publish(topic, message, qos=1, retain=False)
        

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 
