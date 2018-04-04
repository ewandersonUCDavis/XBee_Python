#This script adds two new features to tes12.py. 1) It reads turbine parameters from an input file inputFile.txt instead of defining those parameters in this script 2) 


import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
from random import *
import time
import threading
import csv

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
#addr2name = {
#	"\x00\x13\xA2\x00\x41\x27\xCA\xE8" : "Turbine1",
#	"\x00\x13\xA2\x00\x41\x54\xD5\x86" : "Turbine2",
#	"\x00\x13\xA2\x00\x41\x27\xCA\xEC" : "Turbine3"
#}   

mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "EoF9kjhJz0ESHHnTJmsD" #this is the access token for the thingsboard gateway device

topicAttr = "v1/gateway/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
topicGtwyAttr = 'v1/devices/me/attributes'
topicTelem = "v1/gateway/telemetry" #This is the topic for sending telemetry through a gateway in thingsboard  
topicConnect = "v1/gateway/connect"
rpcTopic = "v1/devices/me/rpc/request/+"  #Come back to this***********


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.subscribe(rpcTopic)
    MQTT.subscribe('v1/devices/me/attributes/response/+')
    #MQTT.publish(topicGtwyAttr,json.dumps({'turbineOnOff_switch':True, 'safety_switch': True}), qos=1, retain=True) #Comment this out after the first time you run the program. The first time you need it to establish these attributes.



# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
	global MQTT_message, new_MQTT_message
	print 'Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload)
	MQTT_message = msg
	new_MQTT_message = True 
	
def readTurbineInputFile(): #This reads the turbine parameter input file inputFile.txt and formats the data in the necessary libraries that will be used by other parts of this program.
	addr2name = {}
	name2addr = {}
	with open('inputFile.txt') as f : #read input file and store data in the list turbArrayProps
		reader = csv.reader(f, delimiter="\t")
		turbArrayProps = list(reader)
	for i in range(1, len(turbArrayProps)): #process each row in input file
		name = turbArrayProps[i][0]
		address = '0013a200'+turbArrayProps[i][1]
		address = address.lower() #converts all letters to lower case (in case it isn't entered that way in the input file)
		address = address.decode('hex')
		print(address)
		latitude = turbArrayProps[i][2]
		longitude = turbArrayProps[i][3]
		addr2name[address] = name #to find a turbine name from the remote XBee address
		name2addr[name] = address #The reverse of the previous dictionary. Used to find the remote XBee address from a turbine name
		MQTT.publish(topicConnect, json.dumps({'device':name})) #Tell thingsboard that this turbine is connected
		MQTT.publish(topicAttr,json.dumps({name:{'latitude':latitude,'longitude':longitude}})) #Tell thingsboard the position of this turbine
	return addr2name, name2addr

		
def attribute_message(data): #Process a message from thingsboard in response to an attribute value request
    global safety_switch, turbineOnOff_switch
    print('recieved current switch status from Thingsboard')
    data = data.get('client')
    safety_switch = data.get('safety_switch')
    turbineOnOff_switch = data.get('turbineOnOff_switch')
    
def switch_message(data): #process an RPC message received from one of the thingsboard switches.
	global safety_switch, turbineOnOff_switch
	print('RPC Switch message recieved')
	params = data.get("params")
	method = data.get("method")
	if (method == "set_safety_switch"): #the safety switch has been toggled
		print('method == set_safety_switch')
		safety_switch = params
		message = {'safety_switch':safety_switch}
		MQTT.publish(topicGtwyAttr, json.dumps(message), qos=1, retain=True)
	elif (method == "set_turbineOnOff_switch") & (safety_switch): #the on/off switch has been toggled, but the safety is on
		print('method == set_turbineOnOff_switch and safety_switch == True')
		if (turbineOnOff_switch != params): #If the thingsboard switch has been flipped
			message = {'turbineOnOff_switch':params}
			pub = MQTT.publish(topicGtwyAttr, json.dumps(message), qos=1, retain=True) #toggle the thingsboard value of turbineOnOff_switch
			pub.wait_for_publish()
			message = {'turbineOnOff_switch':turbineOnOff_switch}
			pub = MQTT.publish(topicGtwyAttr, json.dumps(message), qos=1, retain=True) #then toggle it back
	elif (method == "set_turbineOnOff_switch") & (safety_switch == False): #the on/off switch has been toggled, and the safety is off
		print('method == set_turbineOnOff_switch and safety_switch == False')
		message = {'turbineOnOff_switch':params}
		turbineOnOff_switch = params
		MQTT.publish(topicGtwyAttr, json.dumps(message), qos=1, retain=True) #toggle the switch
		#put code here to initiate the turbine start/stop sequence
	else:
		print('correct switch method not found!')

def listener():
	while True:
		time.sleep(.1)
		global MQTT_message, new_MQTT_message	
		if new_MQTT_message:
			new_MQTT_message = False
			if MQTT_message.topic[0:34] == 'v1/devices/me/attributes/response/': #This message is a response to our switch status attribute request (only happens when we connect to the MQTT server)
				attribute_message(json.loads(MQTT_message.payload)) 
			elif MQTT_message.topic[0:26] == 'v1/devices/me/rpc/request/' : #This is an RPC message from one of the switches
				switch_message(json.loads(MQTT_message.payload)) 
			else:
				print('Message type not recognized!!!')



MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

MQTT.loop_start()

#MQTT.publish(topicConnect, "{'device':'Turbine1'}")
#MQTT.publish(topicConnect, "{'device':'Turbine2'}")
#MQTT.publish(topicConnect, "{'device':'Turbine3'}")
#MQTT.publish(topicAttr,"{Turbine1:{latitude: 35.0714872, longitude: -118.3362909},Turbine2:{latitude: 35.0720557, longitude: -118.3350022},Turbine3:{latitude: 35.0733736, longitude: -118.3315367}}")
MQTT.publish('v1/devices/me/attributes/request/1', '{"clientKeys":"safety_switch,turbineOnOff_switch"}', qos=1, retain=True)

addr2name, name2addr = readTurbineInputFile()


#print(addr2name)
#print(name2addr)

new_MQTT_message = False
T = threading.Thread(target=listener)
T.daemon = True #This means the thread will automatically quit if main program quits
T.start()

serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.

while True:
    try:
		response = xbee.wait_read_frame() #Wait for an API frame to arrive. Note: this blocks while it is waiting.
		if ('samples' in response): #Is this a DIO sample frame?
			IO_Data = response.get('samples')[0] #The .get() outputs a 1 element long list, where the element is a dict. Adding the [0] stores the dict in IO_Data instead of the list containing the dict.
			dataKeys = IO_Data.keys() #get a list of all the data samples IO_Data
			turbineName = addr2name.get(response.get('source_addr_long')) #find the name of the turbine that sent this message
			print(turbineName)
			#print(IO_Data)
			#rename data. (- symbols cause problems in thingsboard)
			for X in dataKeys:
				IO_Data[pinMap.get(X)]=IO_Data.pop(X)
			print(IO_Data)
			#Publish pin 3 & 4 status to thingsboard attributes over MQTT 
			message = {turbineName: IO_Data} #Convert IO_Data to a string (format required by publish).
			print(message)
			MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True)
			
			ts = 1000*time.time()
			#print(ts)
			#print(type(ts))
			Power = randint(80, 100) #We're not actually measuring power at this point, so I'm going to generate a random number and pretent it's the production.
			messageTelem = {turbineName:[{'ts':ts, 'values':{'Power':Power}}]}
			print(messageTelem)
			print(topicTelem)
			MQTT.publish(topicTelem, json.dumps(messageTelem), qos=1, retain=True)
			
		elif ('rf_data' in response): #Is this a power meter pulse count? 
			turbineName = addr2name.get(response.get('source_addr_long')) #find the name of the turbine that sent this message
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
