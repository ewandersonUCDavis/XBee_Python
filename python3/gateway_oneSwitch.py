#This is my attempt at a complete gateway progtam serving as an interface between the thingsboard.io based user interface and the xbee based turbine network.

import serial #for connecting to local xbee through serial port
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress #for interacting with xbee network
from digi.xbee.io import IOLine, IOMode, IOValue #for processing DIO data from the xbee network
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
		address = '0013A200'+turbArrayProps[i][1]
		address = address.upper() #convert address to upper case if it isn't already.
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

#This processes RPC messages received from the thingsboard switches    
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
		for name in name2addr.keys():
			print(name2addr)
			print(name)
			try:
				if (params == True):
					print('Starting ',name)
					remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string(name2addr.get(name)))
					xbee.send_data(remote, "start")
				elif (params == False):
					print('Stoping ',name)
					remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string(name2addr.get(name)))
					xbee.send_data(remote, "stop")
				MQTT.publish(topicAttr, json.dumps({name: {'responsive':'true'}}), qos=1, retain=True) #tell thingsboard that the turbine controller did respond to the start/stop request
			except:
				print(name,' not found!')
				MQTT.publish(topicAttr, json.dumps({name: {'responsive':'false'}}), qos=1, retain=True) #tell thingsboard that the turbine controller did not respond to the start/stop request
				#Consider setting some indicator in thingsboard that turbine was unresponsive
		MQTT.publish(topicGtwyAttr, json.dumps(message), qos=1, retain=True) #toggle the switch
	else:
		print('correct switch method not found!')

# this loop runs in parallel to the main loop using threading. It continuously listens for messages from thingsboard then calls the appropriate function to process the message.
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

MQTT.publish('v1/devices/me/attributes/request/1', '{"clientKeys":"safety_switch,turbineOnOff_switch"}', qos=1, retain=True)

addr2name, name2addr = readTurbineInputFile()


new_MQTT_message = False
T = threading.Thread(target=listener)
T.daemon = True #This means the thread will automatically quit if main program quits
T.start()
		

###################################################################################
### Part 2: XBee stuff
################################################################################### 
	
faultMap = {
	IOLine.DIO2_AD2:'fault_1', 
	IOLine.DIO3_AD3:'fault_2', 
	IOLine.DIO4_AD4:'fault_3', 
	IOLine.DIO6:'fault_4'}  
		
def data_receive_callback(xbee_message): #Called when the local XBee receives a data message. This is used for receiving power production data.
	print('pulse count received')
	pulseCount = (256*xbee_message.data[0]+xbee_message.data[1]) #number of pulses counted in the last 15 minutes
	print("From",xbee_message.remote_device.get_64bit_addr()," >> Pulse count = ",pulseCount)
	pulsePower = .05 #.05 kW-hr per meter pulse 
	avgPower = pulseCount*pulsePower*4 #Average power production over the last 15 minutes.
	turbineName = addr2name[str(xbee_message.remote_device.get_64bit_addr())] #find the name of the turbine that sent this message
	message = {turbineName:[{'ts':1000*xbee_message.timestamp, 'values':{'Power':avgPower}}]}
	print(message)
	MQTT.publish(topicTelem, json.dumps(message), qos=1, retain=True)

def io_sample_callback(io_sample, remote_xbee, send_time): #Called when the local XBee receives an IO Sampling message. Used to detect changes in rotor brake or turbine faults.
	print("IO sample received at time %s." % str(send_time))
	if (io_sample.get_digital_value(IOLine.DIO1_AD1) == IOValue.HIGH): #first process the part of the data telling us if the turbine is on or off
		IOData = {'brake_on':'true'}
	else:
		IOData = {'brake_on':'false'}
	any_fault = 'false' #then process the part of the data telling us if any faults were detected. 
	for x in faultMap.keys() : #we're going to cycle through all the key:value pairs in faultMap
		if (io_sample.get_digital_value(x) == IOValue.HIGH):
			IOData[faultMap[x]] = 'true'
			any_fault = 'true'
		else:
			IOData[faultMap[x]] = 'false'
	IOData['any_fault'] = any_fault
	print('IOData: ',IOData)
	#finally, put everything together and publish the data to thingsboard
	turbineName = addr2name[str(remote_xbee.get_64bit_addr())] #find the name of the turbine that sent this message
	print(turbineName)
	message = {turbineName: IOData}
	print(message)
	MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True)

xbee = XBeeDevice('/dev/tty.usbserial-A505N9YU', 9600) 
xbee.open()

try:
	xbee.add_data_received_callback(data_receive_callback)		# Subscribe to data message reception (for power pulse count data).
	xbee.add_io_sample_received_callback(io_sample_callback)	# Subscribe to IO samples reception.
	print("Waiting for data...\n")
	input()
finally:
	if xbee is not None and xbee.is_open():
		xbee.close()
