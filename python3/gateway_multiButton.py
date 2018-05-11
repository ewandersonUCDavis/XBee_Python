#This code serves as an interface between the thingsboard.io based user interface and the xbee based turbine network. This version was written specifically for the user interface that has individual on/off switches for each turbine.

import serial #for connecting to local xbee through serial port
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress #for interacting with xbee network
from digi.xbee.io import IOLine, IOMode, IOValue #for processing DIO data from the xbee network
import paho.mqtt.client as mqtt #for interacting with thingsboard.io through mqtt messaging protocol
import json #makes converting between json libraries and strings easier. This helps processing mqtt messages.
import time #Is this still needed?
import threading #is this still needed?
import csv #Allows us to read in comma seperated value (csv) data files. Used to read inputFile.txt


###################################################################################
### Part 0: User specified parameters
###################################################################################
systemDemo = True #Set this to true if the remote XBees are not connected to anything, but we still want to send output to thingsboard. It will make up fake power production values
localXBeePort = '/dev/tty.usbserial-A505N9YU'

faultMap = {
	IOLine.DIO2_AD2:'fault_1', 
	IOLine.DIO3_AD3:'fault_2', 
	IOLine.DIO4_AD4:'fault_3', 
	IOLine.DIO6:'fault_4'}  

###################################################################################
### Part 1: MQTT stuff
###################################################################################
mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on cloud computing
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "EoF9kjhJz0ESHHnTJmsD" #this is the access token for the thingsboard gateway device

#mqttBroker = "http://wind-stream.dynu.net" #This is the instance of thingsboard that we installed on a linux box
#mqttUserName     = "HEvnDc1Hei0VFQdkXxqN" #this is the access token for the thingsboard gateway device

topicAttr = "v1/gateway/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
topicTelem = "v1/gateway/telemetry" #This is the topic for sending telemetry through a gateway in thingsboard  
topicConnect = "v1/gateway/connect"

# The callback for when we recieve a CONNACK response from the MQTT server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    MQTT.subscribe("v1/gateway/rpc") #Subscribing to receive RPC requests

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
		print("i = ",str(i))
		name = turbArrayProps[i][0]
		address = '0013A200'+turbArrayProps[i][1]
		address = address.upper() #convert address to upper case if it isn't already.
		latitude = turbArrayProps[i][2]
		longitude = turbArrayProps[i][3]
		addr2name[address] = name #to find a turbine name from the remote XBee address
		name2addr[name] = address #The reverse of the previous dictionary. Used to find the remote XBee address from a turbine name
		MQTT.publish(topicConnect, json.dumps({'device':name})) #Tell thingsboard that this turbine is connected
		MQTT.publish(topicAttr,json.dumps({name:{'latitude':latitude,'longitude':longitude}})) #Tell thingsboard the position of this turbine
		MQTT.publish(topicAttr,json.dumps({name:{'startButton':False}}), qos=1, retain=True) #Comment this out after the first time you run the program. The first time you need it to establish these attributes.
		MQTT.publish(topicAttr,json.dumps({name:{'stopButton':False}}), qos=1, retain=True) #Comment this out after the first time you run the program. The first time you need it to establish these attributes.
	return addr2name, name2addr

#This processes RPC messages received from the thingsboard switches    
def switch_message(data): #process an RPC message received from one of the thingsboard switches.
	global safety_switch, turbineOnOff_switch
	print('RPC Switch message recieved')
	name = data.get("device")
	method = data.get("data").get("method")
	if (method == "startButton"):
		print('Starting ',name)
		remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string(name2addr.get(name)))
		xbee.send_data(remote, "start") #Send start message to remote XBee
		pub = MQTT.publish(topicAttr, json.dumps({name:{'startButton':True}}), qos=1, retain=True) #toggle the thingsboard value of startButton
		pub.wait_for_publish()
		pub = MQTT.publish(topicAttr, json.dumps({name:{'startButton':False}}), qos=1, retain=True) #then toggle it back
	elif (method == "stopButton"):
		print('Stoping ',name)
		remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string(name2addr.get(name)))
		xbee.send_data(remote, "stop")
		pub = MQTT.publish(topicAttr, json.dumps({name:{'stopButton':True}}), qos=1, retain=True) #toggle the thingsboard value of stopButton
		pub.wait_for_publish()
		pub = MQTT.publish(topicAttr, json.dumps({name:{'stopButton':False}}), qos=1, retain=True) #then toggle it back

# this loop runs in parallel to the main loop using threading. It continuously listens for messages from thingsboard then calls the appropriate function to process the message.
def listener():
	while True:
		time.sleep(.1)
		global MQTT_message, new_MQTT_message	
		if new_MQTT_message:
			new_MQTT_message = False
			if MQTT_message.topic[0:14] == 'v1/gateway/rpc' : #This is an RPC message from one of the switches
				print("message recieved")
				switch_message(json.loads(MQTT_message.payload)) 
			else:
				print('Message type not recognized!!!')
				
				
MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

addr2name, name2addr = readTurbineInputFile()

MQTT.loop_start()

new_MQTT_message = False
T = threading.Thread(target=listener)
T.daemon = True #This means the thread will automatically quit if main program quits
T.start()
		
###################################################################################
### Part 2: XBee stuff
################################################################################### 
		
def data_receive_callback(xbee_message): #Called when the local XBee receives a data message. This is used for receiving power production data.
	print('pulse count received')
	pulseCount = (256*xbee_message.data[0]+xbee_message.data[1]) #number of pulses counted in the last 15 minutes
	print("From",xbee_message.remote_device.get_64bit_addr()," >> Pulse count = ",pulseCount)
	if (systemDemo == True):
		pulseCount = randint(400, 500) #We're not actually measuring power at this point, so I'm going to generate a random number and pretent it's the production.
		print("systemDemo enabled. Simulated pulseCount = ",str(pulseCount))
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

xbee = XBeeDevice(localXBeePort, 9600) 
xbee.open()

try:
	xbee.add_data_received_callback(data_receive_callback)		# Subscribe to data message reception (for power pulse count data).
	xbee.add_io_sample_received_callback(io_sample_callback)	# Subscribe to IO samples reception.
	print("Waiting for data...\n")
	input()
finally:
	if xbee is not None and xbee.is_open():
		xbee.close()
