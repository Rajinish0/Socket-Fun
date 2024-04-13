from socket import *
import time, threading, uuid, pickle, random
from constants import S_constants as S, C_constants as C
from utils import *
from player import Player

HOST = '' ## LOCALHOST
PORT = 50007
MAX_CONC = 5
players = {}
playerConns = {}
threads = []
CHUNK_SZ = 1024
W, H = 20, 20

def now():
	return time.ctime(time.time())

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
	return newid

def sendPos(conn, id_):
	r = (random.randint(1, 200), random.randint(1, 200) )
	print(f'SENDING {r}')
	sendData(conn, r)

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

def sendObjToOthers(id_, obj):
	global playerConns
	for uid, conn in playerConns.items():
		if id_ == uid: continue
		print(f'seding obj to {id_}')
		conn.send(S.FOREIGN_PLAYERS)
		sendData(conn, id_)
		sendData(conn, obj)

def parseMsg(conn, msg):
	global players, playerConns
	#print(f'parsing {msg, msg[0], C.CONNECT, msg[0] == C.CONNECT}')
	if len(msg) == 0: return
	opt = msg[0:1]
	match opt:
		case C.CONNECT: 
			print('SENDING ID')
			return sendId(conn)
		case C.GET: 
			handleGet(conn)
		case C.STORE:
			obj = getData(conn)
			id_ = getData(conn)
			# print('SENDING OBJECT TO EVERYONE')
			# print(playerConns)
			sendObjToOthers(id_, obj)
			print('player conns now: ', playerConns)
			players[id_] = obj
			playerConns[id_] = conn
			print(f'GOT obj from {id_}')
		# case C.UPDATE:
		# 	pass
	return None

def sendDelToOthers(id_):
	global playerConns
	for uid, conn in playerConns.items():
		if uid == id_: continue
		conn.send(S.DEL)
		sendData(conn, id_)

def handler(conn, addr):
	global players
	id_ = None
	while True:
		msg = conn.recv(1)
		print(f'RECEVIED {msg} from {addr}')
		#print(f"Recevied {msg}")
		if not msg: break
		prse = parseMsg(conn, msg)
		id_ = (id_ or prse)
	print(f'Closing connection with {addr}')
	sendDelToOthers(id_)
	del players[id_]
	del playerConns[id_]
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


if __name__ == '__main__':
	sckobj = socket(AF_INET, SOCK_STREAM) # tcp/ip
	sckobj.bind((HOST, PORT))
	sckobj.listen(MAX_CONC) ## at most 5 concurrent connections
	run()

	for thread in thread:
		thread.join()
	
	print(f'Server exiting at {now()}')
