import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
import time
import threading


mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "OKYS34HzHCWOHWSckxL4" #this is the access token for the thingsboard gateway device

topicAttr = "v1/devices/me/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
rpcTopic = "v1/devices/me/rpc/request/+"  #Come back to this***********
rpcResponseTopic = "v1/devices/me/rpc/response/"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.subscribe(rpcTopic)
    MQTT.subscribe('v1/devices/me/attributes/response/+')
    print('one')

    
    
    
    
# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
	global MQTT_message, new_MQTT_message
	print('on_message')
	print 'Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload)
	MQTT_message = msg
	new_MQTT_message = True


        
        
def attribute_message(data):
    global safety_switch, turbineOnOff_switch
    print('recieved current switch status from Thingsboard')
    data = data.get('client')
    safety_switch = data.get('safety_switch')
    turbineOnOff_switch = data.get('turbineOnOff_switch')
    
def switch_message(data):
	global safety_switch, turbineOnOff_switch
	print(' ')
	print('RPC Switch message recieved')
	print('safety_switch type: '+str(type(safety_switch)))
	print('turbineOnOff_switch type: '+str(type(turbineOnOff_switch)))
	params = data.get("params")
	method = data.get("method")
	if (method == "set_safety_switch"): #the safety switch has been toggled
		print('method == set_safety_switch')
		safety_switch = params
		print('safety_switch = '+str(safety_switch))
		print(type(safety_switch))
		message = {'safety_switch':safety_switch}
		MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True)
	elif (method == "set_turbineOnOff_switch") & (safety_switch): #the on/off switch has been toggled, but the safety is on
		print('method == set_turbineOnOff_switch and safety_switch == True')
		if (turbineOnOff_switch != params): #If the thingsboard switch has been flipped
			message = {'turbineOnOff_switch':params}
			print(message)
			pub = MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True) #toggle the thingsboard value of turbineOnOff_switch
			pub.wait_for_publish()
			message = {'turbineOnOff_switch':turbineOnOff_switch}
			print(message)
			pub = MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True) #then toggle it back
	elif (method == "set_turbineOnOff_switch") & (safety_switch == False): #the on/off switch has been toggled, and the safety is off
		print('method == set_turbineOnOff_switch and safety_switch == False')
		message = {'turbineOnOff_switch':params}
		turbineOnOff_switch = params
		MQTT.publish(topicAttr, json.dumps(message), qos=1, retain=True) #toggle the switch
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

#def talker():
#	while True:
#		print('Hello!')
#		time.sleep(10)
    
    


    
    
MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

MQTT.connect(mqttBroker)
MQTT.publish('v1/devices/me/attributes/request/1', '{"clientKeys":"safety_switch,turbineOnOff_switch"}', qos=1, retain=True)

MQTT.loop_start()

new_MQTT_message = False
print('one')
T = threading.Thread(target=listener)
T.daemon = True #This means the thread will automatically quit if main program quits
T.start()
#print('two')
#B = threading.Thread(target=talker)
#B.start()

while True:
	print('Hello!')
	time.sleep(10)



