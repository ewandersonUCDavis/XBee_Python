from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress, XBeeMessage
from struct import *
import json
from digi.xbee.io import IOLine, IOMode, IOValue

xbee = XBeeDevice('/dev/tty.usbserial-A505N9YU', 9600)

xbee.open()
print(xbee.get_node_id())


try:


	def data_receive_callback(xbee_message):
			print("pulse count data recieved")
			pulseCount = (256*xbee_message.data[0]+xbee_message.data[1])
			print("From",xbee_message.remote_device.get_64bit_addr()," >> Pulse count = ",pulseCount)
			print(xbee_message.remote_device.get_node_id())


	def io_sample_callback(io_sample, remote_xbee, send_time):
			print("IO sample:")
			print("IO sample received at time %s." % str(send_time))
			print("IO sample:")
			print(str(io_sample))
			print(str(remote_xbee))
			print(type(remote_xbee))
			print(remote_xbee.get_64bit_addr())
			print(type(remote_xbee.get_64bit_addr()))
			print(remote_xbee.get_node_id())
			b = io_sample.get_digital_value(IOLine.DIO1_AD1)
			print(b)
			print(type(b))
			if (b == IOValue.LOW):
				print('Hi!')


	xbee.add_data_received_callback(data_receive_callback)

	# Subscribe to IO samples reception.
	xbee.add_io_sample_received_callback(io_sample_callback)	

	print("Waiting for data...\n")
	input()

finally:
	print('finally')
	stop = True
	if xbee is not None and xbee.is_open():
		print('closing xbee')
		xbee.close()
		print('xbee closed')
		

