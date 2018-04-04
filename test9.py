import struct

Library = {
	"D6" : "turbine1",
	"D5" : "turbine2",
	"D4" : "turbine3",
	"D3" : "turbine5",
	"D2" : "turbine4",
	"D1" : "turbine6"
}
print('********************************')
print('********************************')
print(Library.keys())
print('********************************')
print(Library)
print('********************************')
keys = Library.keys()
print(keys)
print('********************************')

	
for i in keys:
	Library['T1-'+i]=Library.pop(i)
	print(Library)

print('********************************')
print(Library)
print('********************************')
print('********************************')


#A = "\xca\xe8"
#A = '\x01\xff'
B = struct.unpack('>H',A)

print(B)
print(type(B))
print(B[0])
