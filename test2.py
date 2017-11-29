#This extends test1.py. After receiving an API frame it sends the pin statuses to an MQTT server. 

import serial
from xbee import XBee, ZigBee
import paho.mqtt.client as mqtt

mqttBroker = "demo.thingsboard.io"
mqttClientId     = "ewanderson"
mqttUserName     = "HgQrDJl1F8Hgr1BpfT54" 

#MQTT = mqtt.Client("ewanderson",clean_session=False)
#MQTT.username_pw_set("HgQrDJl1F8Hgr1BpfT54") 
#MQTT.connect("demo.thingsboard.io")

MQTT = mqtt.Client(mqttClientId,clean_session=False)
MQTT.username_pw_set(mqttUserName) 
MQTT.connect(mqttBroker)

MQTT.loop_start()
topic = "v1/devices/me/telemetry" #I'm not sure why this is the topic. It came from thingsboard demo

serial_port = serial.Serial('/dev/tty.usbserial-A505N9YU', 9600)
xbee = ZigBee(serial_port) #Setting this up as an XBee object doesn't work. I think the XBee pros use the same APi frame as the Zigbees, not the API frame that earlier XBees used.

while True:
    try:

        response = xbee.wait_read_frame() #Wait for an API frame to arrive. Note: this blocks while it is waiting.

        IO_Data = response.get('samples')[0] #The .get() outputs a 1 element long list, where the element is a dict. Adding the [0] stores the dict in IO_Data instead of the list containing the dict.

        
        #Publish pin 4 status to thingsboard over MQTT 
        message = str(IO_Data) #Convert IO_Data to a string (format required by publish).
        print message
        MQTT.publish(topic, message, qos=1, retain=False)

    except KeyboardInterrupt:
    
        break

serial_port.close()


# Hi and Low address of receiving XBee
# 13A200
# 4127CAEE 
