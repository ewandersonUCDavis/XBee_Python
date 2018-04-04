#I'm using this script to do some debugging to figure out why I'm having rrouble sending telemetry through a gateway.


import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt
import json
from random import *


mqttBroker = "192.155.83.191" #This is the instance of thingsboard that we installed on ???
mqttClientId     = "ewanderson" #This can be anything, but you have to pick a unique Id so thingsboard can keep track of what messages it has already sent you.
mqttUserName     = "A1_TEST_TOKEN" #this is the access token for the thingsboard gateway device

topicTelem = "v1/gateway/telemetry" #This is the topic for sending telemetry through a gateway in thingsboard  



# The callback for when the client receives a CONNACK response from the server.
def on_connect(MQTT, userdata, flags, rc):
    print("Connected with result code "+str(rc)) #result code 0 means sucessfuly connected

#m2 = "{\"Device A\": [{ \"ts\": 1483228801000, \"values\": { \"temperature\": 43, \"humidity\": 82 }}], \"Device B\": [{ \"ts\": 1483228800000, \"values\": { \"temperature\": 42, \"humidity\": 80 }}]}" 

m2 = "{\"Device A\":{\"temperature\":43, \"humidity\": 82}, \"Device B\":{\"temperature\":42, \"humidity\":80}}"

print(m2)



MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)
MQTT.on_connect = on_connect #call on_connect() when MQTT connects to the mqtt broker.

MQTT.loop_start()


print(type(m2))
print(topicTelem)
MQTT.publish(topicTelem, m2, qos=1, retain=False)		

MQTT.disconnect()
# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 


