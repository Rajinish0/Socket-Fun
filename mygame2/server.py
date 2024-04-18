from socket import *
import time, threading, uuid, pickle, random, sys
from constants import S_constants as S, C_constants as C, W, H
from utils import *
from player import Player

HOST = '' ## LOCALHOST
PORT = 50007
MAX_CONC = 5
players = {}
playerConns = {}
threads = []
CHUNK_SZ = 1024
foodPos = (400, 300)

# outputFile = open('serverlogs.txt', 'w')
# sys.stdout = outputFile

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
	pos = (random.randint(1, 200), random.randint(1, 200) )
	direc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
	print(f'SENDING {pos} {direc} {foodPos}')
	sendData(conn, (pos, direc, foodPos) )

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

def sendUpdateToOthers(id_, obj):
	for uid, conn in playerConns.items():
		if id_ != uid:
			conn.send(S.UPDATE)
			sendData(conn, id_)
			sendData(conn, obj)

def sendFoodUpadteToEveryone():
	msg = S.FOOD_UPDATE
	for id_, conn in playerConns.items():
		conn.send(msg)
		sendData(conn, foodPos)

def parseMsg(conn, msg, sendLock):
	global players, playerConns, foodPos
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
			print('player conns now: ', playerConns)
			players[id_] = obj
			playerConns[id_] = conn
			with sendLock:
				sendObjToOthers(id_, obj)
			print(f'GOT obj from {id_}')
		case C.UPDATE:
			obj = getData(conn)
			id_ = getData(conn)
			players[id_] = obj
			with sendLock:
				sendUpdateToOthers(id_, obj)
		case C.VERIFY:
			# print('YES GOT VERIFY')
			obj = getData(conn)
			id_ = getData(conn)
			players[id_] = obj
		case C.EAT:
			foodPos = (random.randint(1, W), random.randint(1, H))
			with sendLock:
				sendFoodUpadteToEveryone()
			# conn.send(S.ACPT)
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
	sendLock = threading.Lock()
	while True:
		msg = conn.recv(1)
		if not msg: break
		prse = parseMsg(conn, msg, sendLock)
		id_ = (id_ or prse)

	print(f'Closing connection with {addr}')
	with sendLock:
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
