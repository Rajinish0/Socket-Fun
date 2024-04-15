from socket import *
from constants import S_constants as S, C_constants as C
import pickle, uuid, time, pygame, threading, sys
from utils import *
from player import Player


HOST = 'localhost'
PORT = 50007
UNQ_LEN = 36

# outputFile = open('clientlogs.txt', 'w')
# sys.stdout = outputFile

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
	# print(f'SENT {data} to server')

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
		self.sendLock = threading.Lock()
		self.getLock = threading.Lock()
		# self.sckobj.settimeout(0.5)
		self.initalizeRequestListener()
		self.initalizePositionVerifier()
		self.dx = 0.1
		self.dy = 0.1
		self.run = True
		self.display = pygame.display.set_mode((800, 600))

	def initPlayer(self):
		msg = C.GET + C.POS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		pos, direc = parseData(self.sckobj, data)
		self.player = Player(pos, direc)
		print(f'received pos= {pos}')

	def positionVerifier(self):
		while True:
			with self.sendLock:
				# self.sckobj.settimeout(2)
				msg = C.VERIFY
				self.sckobj.send(msg)
				sendData(self.sckobj, (self.player.pos,
									   self.player.dir))
				sendData(self.sckobj, self.uid)
			time.sleep(0.2)
				# rmsg = self.sckobj.recv(1)
				# match rmsg[0:1]:					
					# case S.ACPT:
						# pass
						# print('YES IT GOT ACCEPTED')
					# case S.RJCT:
						# pass
				# self.sckobj.settimeout(0.5)
			# time.sleep(0.5)


	def requestListener(self):
		while True:
			with self.getLock:
				msg = self.sckobj.recv(1)
				# print(f'received {msg}')
				match msg[0:1]:
					case S.FOREIGN_PLAYERS:
						print('PARSING OBJ')
						id_ = getData(self.sckobj)
						(pos, direc) = getData(self.sckobj)
						self.foreigners[id_] = Player(pos, direc)
						print('PARSED OBJ')
					case S.UPDATE:
						id_ = getData(self.sckobj)
						(pos, direc) = getData(self.sckobj)
						self.foreigners[id_].pos = pos
						self.foreigners[id_].dir = direc
					case S.DEL:
						print('RECVIED REQ TO DELETE')
						idToRem = getData(self.sckobj)
						del self.foreigners[idToRem]
						print(f'DELETED foreigner {idToRem}')
						print(self.foreigners)
					case S.ACPT:
						pass
						# print('YES IT GOT ACCEPTED')
					case S.RJCT:
						pass
				# case S.VERIFY:
				# 	with self.sendLock:
				# 		sendData(self.sckobj, (self.player.pos,
				# 							   self.player.dir) )
					# pass
			# time.sleep(0.5)

	def initalizeRequestListener(self):
		thread = threading.Thread(target=Client.requestListener, args=(self, ))
		thread.daemon = True
		thread.start()

	def initalizePositionVerifier(self):
		thread = threading.Thread(target=Client.positionVerifier, args=(self, ))
		thread.daemon = True
		thread.start()

	def getForeigners(self):
		msg = C.GET + C.FOREIGN_PLAYERS
		self.sckobj.send(msg)
		sendData(self.sckobj, self.uid)
		data = self.sckobj.recv(1+5)
		foreigners = parseData(self.sckobj, data)
		self.foreigners = {
			id_: Player(pos, direc) for id_, (pos, direc) in foreigners.items()
		}
		print(f'GOT FOREIGNERS {self.foreigners}')

	def sendMyUpdate(self):
		msg = C.UPDATE
		with self.sendLock:
			self.sckobj.send(msg)
			sendData(self.sckobj, (self.player.pos, self.player.dir))
			sendData(self.sckobj, self.uid)

	def sendUpdate(self):
		th = threading.Thread(target = Client.sendMyUpdate, args=(self, ))
		th.daemon = True
		th.start()

	def sendMySelf(self):
		msg = C.STORE
		self.sckobj.send(msg)
		sendData(self.sckobj, (self.player.pos, self.player.dir))
		sendData(self.sckobj, self.uid)
		#sendMsg(self.sckobj, myself)

	def pollEvents(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.run = False
		reqUpdt = False
		keys = pygame.key.get_pressed()
		pdir = self.player.dir
		if keys[pygame.K_w]:
			# reqUpdt = self.player.dir != (0, -1)
			self.player.dir = (0, -1)
			# self.player.move( (0, -self.dy) )
		if keys[pygame.K_s]:
			# reqUpdt = self.player.dir != (0, 1)
			self.player.dir = (0, 1)
			# self.player.move( (0,  self.dy) )
			# reqUpdt = True
		if keys[pygame.K_a]:
			# reqUpdt = self.player.dir != (-1, 0)
			self.player.dir = (-1 ,0)
			# self.player.move( (-self.dx ,0) )
			# reqUpdt = True
		if keys[pygame.K_d]:
			# reqUpdt = self.player.dir != (1, 0)
			self.player.dir = (1, 0)
			# self.player.move( (self.dx, 0) )
			# reqUpdt = True

		reqUpdt = (pdir != self.player.dir)
		if reqUpdt:
			self.sendUpdate()

	def mainLoop(self):
		lastTime = time.time()
		while self.run:
			dt = time.time() - lastTime
			lastTime = time.time()
			self.display.fill((0, 0, 0))
			self.pollEvents()
			self.player.update(dt)
			self.player.draw(self.display)
			for foreigner in self.foreigners.values():
				foreigner.update(dt)
				foreigner.draw(self.display)
			# self.player.drawForeigners(self.display, self.foreigners)
			pygame.display.flip()



if __name__ == '__main__':
	c = Client()
	c.mainLoop()
