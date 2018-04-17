from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress, XBeeMessage
from digi.xbee.io import IOLine, IOMode, IOValue


xbee = XBeeDevice('/dev/tty.usbserial-A505N9YU', 9600)

xbee.open()

#remote_xbee = RemoteXBeeDevice(xbee,XBee64BitAddress.from_hex_string("0013A20041574921"))

#a = xbee.send_data(remote_xbee, "Hello")

#print(a)
#while True:
#	print('listening...')
#	message = xbee.read_data(1000)
#	print(message.data)

# Define callback.
def my_data_received_callback(xbee_message):
    print(xbee_message.data)

print('one')
# Add the callback.
xbee.add_data_received_callback(my_data_received_callback)
print('two')


from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
xbee = XBeeDevice('/dev/tty.usbserial-A505NAFC', 9600)
xbee.open()
remote = RemoteXBeeDevice(xbee, XBee64BitAddress.from_hex_string("0013A2004127CAEC"))
xbee.send_data(remote, "Hello!")




from digi.xbee.devices import DigiMeshDevice, RemoteDigiMeshDevice, XBee64BitAddress
xbee = DigiMeshDevice('/dev/tty.usbserial-A505NAFC', 9600)
xbee.open()
remote = RemoteDigiMeshDevice(xbee, XBee64BitAddress.from_hex_string("0013A2004127CAEC"))
xbee.send_data(remote, "Hello!")

