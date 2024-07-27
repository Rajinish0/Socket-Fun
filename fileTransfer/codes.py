ACK  	= b'A'
BYE	 	= b'N'
REQF	= b'D' #req for file
INFO	= b'I' #info for file
REQB	= b'B' #req for block of data
SEND	= b'S' #response to block req, containing block data
DISCONNECT = b'G'


'''
sender		receiver
			 <-REQF
ACK->
INFO->		
			 <-ACK
			 <-REQB
SEND->
			 <-BYE
BYE->
'''





