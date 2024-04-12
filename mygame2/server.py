from socket import *
import time, threading, uuid, pickle
from constants import S_constants as S, C_constants as C

HOST = '' ## LOCALHOST
PORT = 50007
MAX_CONC = 5
players = {}
threads = []
CHUNK_SZ = 1024
W, H = 20, 20

def now():
	return time.ctime(time.time())

def sendMsg(conn, msg):
	for i in range(0, len(msg), CHUNK_SZ):
		conn.send(msg[i:i+CHUNK_SZ])

def receiveMsg(conn, size):
	data = b''
	while size > 0:
		d = conn.recv(min(size, CHUNK_SZ))
		if not d : break
		data += d
		size -= len(d)
	print(f'received {data} from client')
	return data

def parseData(conn, data):
	opt = data[0:1]
	match opt:
		case S.DATA:
			size = int(data[1:])
			parsed = pickle.loads( receiveMsg(conn, size) )
	return parsed

def getData(conn):
	data = conn.recv(1+5)
	return parseData(conn, data)

def sendData(conn, data):
	bytes_ = pickle.dumps(data)
	## TO DO:
	## USE to_bytes
	L = str(len(bytes_)).zfill(5).encode()
	conn.send(S.DATA + L)
	sendMsg(conn, bytes_)

def sendId(conn):
	newid = uuid.uuid4()
	sendData(conn, newid)
	print(f'SENT ID {newid}')

def sendPos(conn, id_):
	print(f'SENDING {(10, 10)}')
	sendData(conn, (10, 10))

def handleGet(conn):
	#if len(msg) == 0: return
	getopt = conn.recv(1)
	print(f'GET GOT OPT {getopt}')
	match getopt:
		case C.POS:
			id_ = getData(conn)
			sendPos(conn, id_)
		case C.FOREIGN_PLAYERS: 
			id_ = getData(conn)
			sendData(conn, players)

def parseMsg(conn, msg):
	#print(f'parsing {msg, msg[0], C.CONNECT, msg[0] == C.CONNECT}')
	if len(msg) == 0: return
	opt = msg[0:1]
	match opt:
		case C.CONNECT: 
			print('SENDING ID')
			sendId(conn)
		case C.GET: 
			handleGet(conn)
		case C.STORE:
			obj = getData(conn)
			id_ = getData(conn)
			print(f'GOT obj from {id_}')

def handler(conn, addr):
	while True:
		msg = conn.recv(1)
		print(f'RECEVIED {msg} from {addr}')
		#print(f"Recevied {msg}")
		if not msg: break
		parseMsg(conn, msg)
	print(f'Closing connection with {addr}')
	conn.close()


def run():
	while True:
		conn, addr = sckobj.accept()
		print(f"Cononected by {addr} at {now()}")
		## handle connection
		thread = threading.Thread(target = handler, args=(conn, addr))
		thread.daemon = True
		threads.append(thread)
		thread.start()

class Player:
	def __init__(self, pos):
		self.pos = pos

if __name__ == '__main__':
	sckobj = socket(AF_INET, SOCK_STREAM) # tcp/ip
	sckobj.bind((HOST, PORT))
	sckobj.listen(MAX_CONC) ## at most 5 concurrent connections
	run()

	for thread in thread:
		thread.join()
	
	print(f'Server exiting at {now()}')
