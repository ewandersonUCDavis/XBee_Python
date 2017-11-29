The purpose of the work in this folder was to investigate how a python script could be used as a gateway between a mesh network  of XBee modules and thingsboard.io. The scripts in this folder will require two Python libraries:

xbee (to interface with XBee modules, )
	-python-xbee documentation (it's not great): http://python-xbee.readthedocs.io/en/latest/#threaded-synchonous-mode
	
paho-mqtt (to send messages to thingsboard.io using the MQTT messaging protocol)
	-paho-mqtt documentation: http://www.eclipse.org/paho/clients/python/docs/
	-general MQTT info: https://www.hivemq.com/mqtt-essentials/

Both can be installed with pip:
pip xbee
pip paho-mqtt

I wrote the test#.py scripts in numerical order. Each one generally builds on the functionality of the one that came before.