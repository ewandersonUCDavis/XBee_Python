#This script has the same functionality as test3.py, but tries to send data to the remote XBee through server side RPC requests instead of through updating a shared attribute.


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
rpcTopic = "v1/devices/me/rpc/request/+"


# We assume that all GPIOs are LOW
gpio_state = {1: False,'Switch': False}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.subscribe('v1/devices/me/rpc/request/+')
     # Sending current GPIO status
    MQTT.publish('v1/devices/me/attributes', get_gpio_status(), 1)
    


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print 'Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload)
    # Decode JSON request
    data = json.loads(msg.payload)
    # Check request method
    if data['method'] == 'getGpioStatus':
        # Reply with GPIO status
        MQTT.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
    elif data['method'] == 'setGpioStatus':
        # Update GPIO status and reply
        set_gpio_status(data['params']['pin'], data['params']['enabled'])
        MQTT.publish(msg.topic.replace('request', 'response'), get_gpio_status(), 1)
        MQTT.publish('v1/devices/me/attributes', get_gpio_status(), 1)

def get_gpio_status():
    # Encode GPIOs state to json
    return json.dumps(gpio_state)


def set_gpio_status(pin, status):
	# Update GPIOs state
	gpio_state[pin] = status;
	if status:#if switchStatus is set to true
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
