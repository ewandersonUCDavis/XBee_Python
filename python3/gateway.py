#This is my attempt at a complete gateway progtam serving as an interface between the thingsboard.io based user interface and the xbee based turbine network.

import serial #for connecting to local xbee through serial port
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress #for interacting with xbee network
import paho.mqtt.client as mqtt #for interacting with thingsboard.io through mqtt messaging protocol
import json #makes converting between json libraries and strings easier. This helps processing mqtt messages.
import time #Is this still needed?
import threading #is this still needed?
import csv #Allows us to read in comma seperated value (csv) data files. Used to read inputFile.txt


###################################################################################
### Part 1: MQTT stuff
###################################################################################
mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "EoF9kjhJz0ESHHnTJmsD" #this is the access token for the thingsboard gateway device

topicAttr = "v1/gateway/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
topicGtwyAttr = 'v1/devices/me/attributes'
topicTelem = "v1/gateway/telemetry" #This is the topic for sending telemetry through a gateway in thingsboard  
topicConnect = "v1/gateway/connect"

# The callback for when we recieve a CONNACK response from the MQTT server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    MQTT.subscribe("v1/devices/me/rpc/request/+") #Subscribing to receive RPC requests
    MQTT.subscribe("v1/devices/me/attributes/response/+") #subscribe to receive answers when we request attributes from the MQTT server

# The callback when we receive a message from the MQTT server.
def on_message(client, userdata, msg):
	global MQTT_message, new_MQTT_message
	print('Topic: ',msg.topic,'\nMessage: ',str(msg.payload))
	MQTT_message = msg
	new_MQTT_message = True 
	
#This reads the turbine parameter input file inputFile.txt and formats the data in the necessary libraries that will be used by other parts of this program.
def readTurbineInputFile(): 
	addr2name = {}
	name2addr = {}
	with open('inputFile.txt') as f : #read input file and store data in the list turbArrayProps
		reader = csv.reader(f, delimiter="\t")
		turbArrayProps = list(reader)
	for i in range(1, len(turbArrayProps)): #process each row in input file
		name = turbArrayProps[i][0]
		address = '0013a200'+turbArrayProps[i][1]
		latitude = turbArrayProps[i][2]
		longitude = turbArrayProps[i][3]
		addr2name[address] = name #to find a turbine name from the remote XBee address
		name2addr[name] = address #The reverse of the previous dictionary. Used to find the remote XBee address from a turbine name
		MQTT.publish(topicConnect, json.dumps({'device':name})) #Tell thingsboard that this turbine is connected
		MQTT.publish(topicAttr,json.dumps({name:{'latitude':latitude,'longitude':longitude}})) #Tell thingsboard the position of this turbine
	return addr2name, name2addr

#This is called once when the program starts. It processes a message from thingsboard containing several attribute values required by other parts of this program.
def attribute_message(data): 
    global safety_switch, turbineOnOff_switch
    print('recieved current switch status from Thingsboard')
    data = data.get('client')
    safety_switch = data.get('safety_switch')
    turbineOnOff_switch = data.get('turbineOnOff_switch')
    

