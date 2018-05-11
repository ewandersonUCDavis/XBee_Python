import paho.mqtt.client as mqtt
import json
import time

mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "EoF9kjhJz0ESHHnTJmsD" #this is the access token for the thingsboard gateway device
#mqttUserName     = "A3QMO5nbq9QnJ53A5w2k" #this is the access token for Turbine1

# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected
    #MQTT.publish("v1/gateway/connect", json.dumps({"device":"Turbine1","device":"Turbine2","device":"Turbine3"})) #This doesn't work. you need a separate connect message for each device connected to the gateway
    MQTT.publish("v1/gateway/connect", json.dumps({"device":"Turbine1"})) #Tell thingsboard that Turbine1 is connected
    MQTT.publish("v1/gateway/connect", json.dumps({"device":"Turbine2"})) #Tell thingsboard that Turbine2 is connected
    MQTT.publish("v1/gateway/connect", json.dumps({"device":"Turbine3"})) #Tell thingsboard that Turbine3 is connected
    MQTT.subscribe("v1/devices/me/rpc/request/+") #subscribe to RPC messages from the gateway
    MQTT.subscribe("v1/gateway/rpc") #subscribe to RPC messages from the gateway
    
    
    
# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
	print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
	print(msg.payload.get(
	

MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.
MQTT.on_message = on_message #call on_message() whenever a message is received from the mqtt broker.

MQTT.loop_start()

while True:
	time.sleep(100) #this is just to keep the script running while MQTT.loop_start() runs in the background. An empty while loop wasn't acceptable to python.
