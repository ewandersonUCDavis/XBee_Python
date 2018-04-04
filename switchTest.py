import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
import time


mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "OKYS34HzHCWOHWSckxL4" #this is the access token for the thingsboard gateway device

topicAttr = "v1/devices/me/attributes" #This is the topic for sending attributes through a gateway in thingsboard  
rpcTopic = "v1/devices/me/rpc/request/+"  #Come back to this***********
rpcResponseTopic = "v1/devices/me/rpc/response/"
#safety_switch = 'true'


# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    #global safety_switch
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    # Subscribing to receive RPC requests
    MQTT.subscribe(rpcTopic)
    #MQTT.subscribe(topicAttr)
    MQTT.subscribe('v1/devices/me/attributes/response/+')
    MQTT.publish('v1/devices/me/attributes/request/1', '{"clientKeys":"safety_switch,turbineOnOff_switch"}', qos=1, retain=True)
    print('one')
    #MQTT.publish(topicAttr,'{"safety_switch": True, "turbineOnOff_switch":True}', qos=1, retain=True)
    #safety_switch = 'True'
    #print('safety_switch = '+safety_switch)
    #MQTT.publish('v1/devices/me/attributes/response/1','{"clientKeys":"safety_switch,onOff_switch"}', qos=1, retain=True)
    #safety_switch = 
    #turbineOnOff_switch = 
    
    
    
    
# The callback for when an RPC message is received from the server.
def on_message(client, userdata, msg):
    print('two')
    global safety_switch, turbineOnOff_switch
    print 'Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload)
    # Decode JSON request
    data = json.loads(msg.payload)
    if msg.topic[0:34] == 'v1/devices/me/attributes/response/': #This message is a response to our switch status attribute request (only happens when we connect to the MQTT server)
    	print('recieved current switch status from Thingsboard')
    	data = data.get('client')
    	safety_switch = str(data.get('safety_switch'))
    	turbineOnOff_switch = str(data.get('turbineOnOff_switch'))
    elif msg.topic[0:26] == 'v1/devices/me/rpc/request/' : #This is an RPC message from one of the switches
    	print(safety_switch)
    	print(turbineOnOff_switch)
    	print('RPC Switch message recieved')
    	params = str(data.get("params"))
    	method = data.get("method")
    	if (method == "set_safety_switch"): #the safety switch has been toggled
    		print('method == set_safety_switch')
    		safety_switch = params
    		print('safety_switch = '+safety_switch)
    		print(type(safety_switch))
    		message = '{"safety_switch":'+safety_switch+'}'
    		MQTT.publish(topicAttr, message, qos=1, retain=True)
    	elif (method == "set_turbineOnOff_switch") & (safety_switch == 'True'): #the on/off switch has been toggled, but the safety is on
    		print('method == set_turbineOnOff_switch and safety_switch == True')
    		message = '{"turbineOnOff_switch":'+params+'}'
    		print(message)
    		a = MQTT.publish(topicAttr, message, qos=1, retain=True) #toggle the switch
    		print(a)
    		if (params == 'True'):
    			message = '{"turbineOnOff_switch":false}' 
    		else:
    			message = '{"turbineOnOff_switch":true}' 
    		print(message)
    		a = MQTT.publish(topicAttr, message, qos=1, retain=True) #but then toggle it right back
    		print(a)
    	elif (method == "set_turbineOnOff_switch") & (safety_switch == 'False'): #the on/off switch has been toggled, and the safety is off
    		print('method == set_turbineOnOff_switch and safety_switch == False')
    		message = '{"turbineOnOff_switch":'+params+'}'
    		turbineOnOff_switch = params
    		MQTT.publish(topicAttr, message, qos=1, retain=True) #toggle the switch
    		#put code here to initiate the turbine start/stop sequence
    	else:
    		print('correct switch method not found!')
    else:
    	print('Message type not recognized!!!')

    
    


    
    
MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

MQTT.loop_start()


#serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
#xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.


while True:
	time.sleep(100) #this is just to keep the script running while MQTT.loop_start() runs in the background. An empty while loop wasn't acceptable to python.
	#response = xbee.wait_read_frame() #Wait for an API frame to arrive. Note: this blocks while it is waiting.
