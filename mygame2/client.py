from socket import *
from constants import S_constants as S, C_constants as C
import pickle, uuid, time, pygame, threading
from utils import *
from player import Player


HOST = 'localhost'
PORT = 50007
UNQ_LEN = 36

'''
{var} means it is some variable
'''
## CLIENT TO SERVER GRAMMAR
'''
	request ::= request_line
	request_line ::= start | options id
	start ::= CONNECT
	id ::= {UUID}
	options ::= GET get_options | STORE data | KMS 
	get_options ::= POS | FOREIGN_PLAYERS
	data ::= DATA CONTENT_LENGTH {DATA}
'''

# CONNECT 		= b'C'
# KMS 			= b'K'
# GET				= b'G'
# POS 			= b'P'
# FOREIGN_PLAYERS = b'F'
# STORE 			= b'S'

# SERVER TO CLIENT GRAMMAR
'''
	response ::= response_line
	response_line ::= KYS | options
	options ::= data | STORE data | DEL id
	id ::= {UUID}
	data ::= DATA CONTENT_LENGTH {ACTUAL_DATA}

'''

# KYS = 'K'
# DATA = 'D'
		
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

def getData(conn):
	data = conn.recv(1+5)
	return parseData(conn, data)

def connectToServer():
	sckobj = socket(AF_INET, SOCK_STREAM)
	sckobj.connect((HOST, PORT))
	msg = C.CONNECT
	sckobj.send(msg)
	## receive uuid
	data = sckobj.recv(6)
	id_ = parseData(sckobj, data)
	return (sckobj, id_)




class Client:
	def __init__(self):
		self.sckobj, self.uid = connectToServer()
		print(f"I received my id {self.uid}")
		self.initPlayer()
		self.getForeigners()
		self.sendMySelf()
		self.initalizeRequestListener()
		self.dx = 0.1
		self.dy = 0.1
		self.run = True
		self.display = pygame.display.set_mode((800, 600))

	def initPlayer(self):
		msg = C.GET + C.POS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		pos = parseData(self.sckobj, data)
		self.player = Player(pos)
		print(f'received pos= {pos}')

	def requestListener(self):
		while True:
			msg = self.sckobj.recv(1)
			print(f'received {msg}')
			match msg[0:1]:
				case S.FOREIGN_PLAYERS:
					print('PARSING OBJ')
					id_ = getData(self.sckobj)
					obj = getData(self.sckobj)
					self.foreigners[id_] = obj
					print('PARSED OBJ')
				case S.DEL:
					print('RECVIED REQ TO DELETE')
					idToRem = getData(self.sckobj)
					del self.foreigners[idToRem]
					print(f'DELETED foreigner {idToRem}')
					print(self.foreigners)

	def initalizeRequestListener(self):
		thread = threading.Thread(target=Client.requestListener, args=(self, ))
		thread.daemon = True
		thread.start()

	def getForeigners(self):
		msg = C.GET + C.FOREIGN_PLAYERS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		self.foreigners = parseData(self.sckobj, data)
		print(f'GOT FOREIGNERS {self.foreigners}')

	def sendUpdate(self):
		th = threading.Thread(target = Client.sendMySelf, args=(self, ))
		th.daemon = True
		th.start()

	def sendMySelf(self):
		msg = C.STORE
		self.sckobj.send(msg)
		sendData(self.sckobj, self.player)	
		sendData(self.sckobj, self.uid)
		#sendMsg(self.sckobj, myself)

	def pollEvents(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.run = False
		reqUpdt = False
		keys = pygame.key.get_pressed()
		if keys[pygame.K_w]:
			self.player.move( (0, -self.dy) )
			reqUpdt = True
		if keys[pygame.K_s]:
			self.player.move( (0,  self.dy) )
			reqUpdt = True
		if keys[pygame.K_a]:
			self.player.move( (-self.dx ,0) )
			reqUpdt = True
		if keys[pygame.K_d]:
			self.player.move( (self.dx, 0) )
			reqUpdt = True

		if reqUpdt:
			self.sendUpdate()

	def mainLoop(self):
		while self.run:
			self.display.fill((0, 0, 0))
			self.pollEvents()
			self.player.draw(self.display)
			self.player.drawForeigners(self.display, self.foreigners)
			pygame.display.flip()



if __name__ == '__main__':
	c = Client()
	c.mainLoop()
