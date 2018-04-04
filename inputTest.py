import csv


with open('inputFile.txt') as f : #read input file and store data in the list turbArrayProps
	reader = csv.reader(f, delimiter="\t")
	turbArrayProps = list(reader)

for i in range(1, len(turbArrayProps)): #re-format the XBee remote addresses to the long address format needed for sending data
	turbArrayProps[i][1] = "\\x00\\x13\\xA2\\x00\\x"+turbArrayProps[i][1][0:2]+"\\x"+turbArrayProps[i][1][2:4]+"\\x"+turbArrayProps[i][1][4:6]+"\\x"+turbArrayProps[i][1][5:7]
	
	print(type(turbArrayProps[i][0]))
	print(type(turbArrayProps[i][1]))
	print(type(turbArrayProps[i][2]))
	print(type(turbArrayProps[i][3]))
