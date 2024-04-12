from socket import *
from constants import S_constants as S, C_constants as C
import pickle, uuid, time


HOST = 'localhost'
PORT = 50007
UNQ_LEN = 36

'''
{var} means it will be dynamically generated 
'''
## CLIENT TO SERVER GRAMMAR
'''
	request ::= request_line
	request_line ::= start | opViktória Joósztions id
	start ::= CONNECT
	id ::= {UID}
	options ::= GET get_options | store CONTENT_LENGTH {DATA} | KMS 
	get_options ::= POS | FOREIGN_PLAYERS
'''

CONNECT 		= b'C'
KMS 			= b'K'
GET				= b'G'
POS 			= b'P'
FOREIGN_PLAYERS = b'F'
STORE 			= b'S'

# SERVER TO CLIENT GRAMMAR
'''
	response ::= response_line
	response_line ::= KYS | options
	options ::= DATA CONTENT_LENGTH {ACTUAL_DATA}
'''

KYS = 'K'
DATA = 'D'

def receiveMsg(sckobj, size, chunksize=1024):
	data = b''
	while size > 0:
		d = sckobj.recv(min(size, chunksize))
		if not d: break
		data += d
		size -= len(d)
	return data

def sendMsg(sckobj, msg, chunksize=1024):
	for i in range(0, len(msg), chunksize):
		sckobj.send(msg[i:i+chunksize])
		
'''
I was thinking of renaming data to object
but since everything in python is a object
pickle.dumps should work nontheless, there underlying assumption
being that I always send pickle-able objects
'''
def sendData(sckobj, data):
	bytes_ = pickle.dumps(data)
	L = str(len(bytes_)).zfill(5).encode()
	sckobj.send(S.DATA + L)
	sendMsg(sckobj, bytes_)
	print(f'SENT {data} to server')

def parseSize(sckobj):
	'''
	im doing this the stupid way for now, later I'll use to_bytes to convert in to bytes
	'''
	data = sckobj.recv(5) # 99999 max bytes of data can be transmitted
	return int(data)

def parseData(sckobj, data):
	option = data[0:1]
	parsed = None
	match option:
		case S.KYS:
			raise Exception("Server killed connection")
		case S.DATA:
			size = int(data[1:1+5])
			parsed = pickle.loads( receiveMsg(sckobj, size)  )
	return parsed

def connectToServer():
	sckobj = socket(AF_INET, SOCK_STREAM)
	sckobj.connect((HOST, PORT))
	msg = CONNECT
	sckobj.send(msg)
	## receive uuid
	data = sckobj.recv(6)
	id_ = parseData(sckobj, data)
	return (sckobj, id_)



class Player:
	def __init__(self, pos):
		self.pos = pos


class Client:
	def __init__(self):
		self.sckobj, self.uid = connectToServer()
		print(f"I received my id {self.uid}")
		self.initPlayer()
		self.getForeigners()
		self.sendMySelf()

	def initPlayer(self):
		msg = GET + POS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		pos = parseData(self.sckobj, data)
		self.player = Player(pos)
		print(f'received pos= {pos}')

	def getForeigners(self):
		msg = GET + FOREIGN_PLAYERS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		self.foreigners = parseData(self.sckobj, data)
		print(f'GOT FOREIGNERS {self.foreigners}')

	def sendMySelf(self):
		msg = STORE
		self.sckobj.send(msg)
		sendData(self.sckobj, self.player)	
		sendData(self.sckobj, self.uid)
		#sendMsg(self.sckobj, myself)



if __name__ == '__main__':
	c = Client()
