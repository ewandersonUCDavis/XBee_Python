#This script does the same thing as test10, but the variable names have been changed to remove "-" characters (they were causing problems in thingsboard).


import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
from random import *
import time


pinMap = {
	'dio-0':'start',
	'dio-1':'stop', 
	'dio-2':'brake_on', 
	'dio-3':'pulse_counter', 
	'dio-4': 'overspeed_fault',
	'dio-7':'vibration_fault', 
	'dio-10':'overtemp_fault', 
	'dio-11':'low_voltage_fault', 
	'dio-12':'other_fault'}



#dict linking remote XBees to the corresponding thingsboard devices The left column is the serial number low (SL) of the remote XBee. The right column is the access token for the corresponding 
turbineList = {
	"\x00\x13\xA2\x00\x41\x27\xCA\xE8" : "Turbine1",
	"\x00\x13\xA2\x00\x41\x54\xD5\x86" : "Turbine2",
	"\x00\x13\xA2\x00\x41\x27\xCA\xEC" : "Turbine3"
}

mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "EoF9kjhJz0ESHHnTJmsD" #this is the access token for the thingsboard gateway device

topicAttr = "v1/gateway/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
topicTelem = "v1/gateway/telemetry" #This is the topic for sending telemetry through a gateway in thingsboard  
topicConnect = "v1/gateway/connect"
rpcTopic = "v1/devices/me/rpc/request/+"  #Come back to this***********


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.publish(topicConnect, "{'device':'Turbine1'}")
    MQTT.publish(topicConnect, "{'device':'Turbine2'}")
    MQTT.publish(topicConnect, "{'device':'Turbine3'}")
    MQTT.publish(topicAttr,"{Turbine1:{latitude: 35.0714872, longitude: -118.3362909},Turbine2:{latitude: 35.0720557, longitude: -118.3350022},Turbine3:{latitude: 35.0733736, longitude: -118.3315367}}")
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
			print(IO_Data)
			#rename data. (- symbols cause problems in thingsboard)
			for X in dataKeys:
				IO_Data[pinMap.get(X)]=IO_Data.pop(X)

			#Publish pin 3 & 4 status to thingsboard attributes over MQTT 
			message = "{"+turbineName+":"+str(IO_Data)+"}" #Convert IO_Data to a string (format required by publish).
			print(message)
			MQTT.publish(topicAttr, message, qos=1, retain=True)
			
			ts = 1000*time.time()
			#print(ts)
			#print(type(ts))
			Power = randint(80, 100) #We're not actually measuring power at this point, so I'm going to generate a random number and pretent it's the production.
			messageTelem = "{\""+turbineName+"\":[{\"ts\":"+str(ts)+", \"values\":{\"Power\":"+str(Power)+"}}]}"
			print(messageTelem)
			print(topicTelem)
			MQTT.publish(topicTelem, messageTelem, qos=1, retain=True)
			
		elif ('rf_data' in response): #Is this a power meter pulse count? 
			turbineName = turbineList.get(response.get('source_addr_long')) #find the name of the turbine that sent this message
			print(turbineName)
			dataName = turbineName+'-15MinPwr'
			#message = '{'+dataName+': '+response.get('rf_data')+'}'
			#MQTT.publish(topicTelem, message, qos=1, retain=False)
        #print response
		#print message
		
		

        

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 

Addresses
