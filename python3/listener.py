from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress, XBeeMessage
from struct import *

xbee = XBeeDevice('/dev/tty.usbserial-A505N9YU', 9600)

xbee.open()
print(xbee.get_node_id())


try:


	def data_receive_callback(xbee_message):
		print("data recieved")
		print(xbee_message)
		print("1")
		print(xbee_message.to_dict())
		print("2")
		print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))
		print("3")
		#print(xbee_message.data.decode())
		#print("4")
		print(xbee_message.data)
		print(unpack('H',xbee_message.data)[0])
		#print("From ",xbee_message.remote_device.get_64bit_addr()," >> ",unpack("h",xbee_message.data.decode()))
		print("5")
		print(xbee_message.data[1])
		print((256*xbee_message.data[0]+xbee_message.data[1]))
		mDict = xbee_message.to_dict()
		print(mDict.get('Data: '))
		print("6")
		print(unpack("h",mDict.get('Data: '))[0])
		print("7")

	def io_sample_callback(io_sample, remote_xbee, send_time):
		print("IO sample:")
		print("IO sample received at time %s." % str(send_time))
		print("IO sample:")
		print(str(io_sample))


	xbee.add_data_received_callback(data_receive_callback)

	# Subscribe to IO samples reception.
	xbee.add_io_sample_received_callback(io_sample_callback)	

	print("Waiting for data...\n")
	input()

finally:
	if xbee is not None and xbee.is_open():
		xbee.close()

