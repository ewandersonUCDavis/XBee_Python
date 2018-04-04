#This script collects DIO data from several remote XBees and sends the data to the correct thingsboard device.


import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json

#dict linking remote XBees to the corresponding thingsboard devices The left column is the serial number low (SL) of the remote XBee. The right column is the access token for the corresponding 
turbineList = {
	"\x00\x13\xA2\x00\x41\x27\xCA\xE8" : "turbine1",
	"\x00\x13\xA2\x00\x41\x54\xD5\x86" : "turbine2"
}

mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "wmxCDkAozyIeqwXCCmt7" #this is an access token that will direct my data to a specific device on thingsboard 

topicAttr = "v1/devices/me/attributes" #This is the topic for attributes in thingsboard  
topicTelem = "v1/devices/me/telemetry" #This is the topic for attributes in thingsboard  

#addr_extended = "\x00\x13\xa2\x00A'\xca\xe8"
#addr_extended = "\x00\x13\xA2\x00\x41\x27\xCA\xE8"
addr = "\xca\xe8"
rpcTopic = "v1/devices/me/rpc/request/+"


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
    	xbee.remote_at(dest_addr_long=addr_extended,command="D4",parameter='\x04') #\x04 means digital low, or False, or LED on (for this pin)
    else: #if switchStatus is set to false
 		xbee.remote_at(dest_addr_long=addr_extended,command="D4",parameter='\x05') #\x05 means digital high, or True, or LED off (for this pin)





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
		
		if ('samples' in response): #Is this a DIO sample frame?
			IO_Data = response.get('samples')[0] #The .get() outputs a 1 element long list, where the element is a dict. Adding the [0] stores the dict in IO_Data instead of the list containing the dict.
			dataKeys = IO_Data.keys() #get a list of all the data samples IO_Data
			turbineName = turbineList.get(response.get('source_addr_long')) #find the name of the turbine that sent this message
			print(turbineName)
			for key in dataKeys:
				IO_Data[turbineName+'-'+key]=IO_Data.pop(key) #Add the turbine name to the beginning of each variable name.
			#Publish pin 3 & 4 status to thingsboard over MQTT 
			message = str(IO_Data) #Convert IO_Data to a string (format required by publish).
			MQTT.publish(topicAttr, message, qos=1, retain=False)
		elif ('rf_data' in response): #Is this a power meter pulse count? 
			turbineName = turbineList.get(response.get('source_addr_long')) #find the name of the turbine that sent this message
			print(turbineName)
			dataName = turbineName+'-15MinPwr'
			message = '{'+dataName+': '+response.get('rf_data')+'}'
			MQTT.publish(topicTelem, message, qos=1, retain=False)
        #print response
		print message
		
		

        

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 

Addresses
