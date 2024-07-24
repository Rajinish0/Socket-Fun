from utils import *
from socket import *
import threading, time
from threading import Lock
import codes
import logging, os
import queue


HOST = "" # localhost
PORT = 50008
CHUNK_SZ = 1024
running = True

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S')

LOGGER = logging.getLogger(os.path.basename(__file__))


messageQ = queue.Queue()

sckobj = socket(AF_INET, SOCK_STREAM) #tcp/ip
sckobj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sckobj.bind((HOST, PORT))
sckobj.listen(5)

connections = {
	"viewers": [],
	"messengers": {}
}
modLock = Lock()

def cleanup(conn):
	conn.close()

def parseData(conn, tLen):
	data = b''
	while (tLen > 0):
		d = conn.recv(min(tLen, CHUNK_SZ))
		if (not d): break
		data += d
		tLen -= len(d)
	return data

def parseName(conn):
	msg = conn.recv(2)
	msgLen = int(msg)
	name = parseData(conn, msgLen)
	return name.decode('utf-8')

threads = []

def now():
	return time.ctime(time.time())

def handler(conn, addr):
	LOGGER.info(f"Handling connection request from {addr}")

	msg = conn.recv(1)
	if not msg: conn.close(); return	
	LOGGER.info(f"received [{msg}] from {addr}")

	with modLock:
		match msg:
			case codes.NAME:
				name = parseName(conn)
				if name == '' or connections['messengers'].get(name) is not None:
					LOGGER.info(f"{addr} wants {name} which is already taken, disconnecting!")
					conn.send(codes.DISCONNECT)
					cleanup(conn)
				else:
					connections['messengers'][name] = conn
					messageQ.put( (name, f"{name} has joined the chat!") )
					conn.setblocking(False) ## only after it is ready
			case _:
				conn.send(codes.DISCONNECT)
				cleanup(conn)
	


def sendMsg(conn, msg):
	for i in range(0, len(msg), CHUNK_SZ):
		conn.send(msg[i:i+CHUNK_SZ])

def checkForNewMessages():
	for name, conn in connections['messengers'].items():
		try:
			msgLen = conn.recv(2) ## they will send msg length first (at most 2 bytes)
			if (msgLen and int(msgLen) > 0):
				msg = parseData(conn, int(msgLen)).decode('utf-8')
				messageQ.put( (name, f"{name}: {msg}") ) 
		except BlockingIOError:
			pass

def sendMessages():
	while not messageQ.empty():
		senderName, msg = messageQ.get()
		msgLen = str(len(msg)).zfill(2)
		fullMsg = ( f'{msgLen}{msg}' ).encode('utf-8')
		'''
		TO DO: 
			decide if it's okay to send the messenger their message back.
			Maybe the input should get deleted after they have written the
			msg.
		'''
		for name, conn in connections['messengers'].items():
			if (name != senderName):
				sendMsg(conn, fullMsg)


def newConnHandler():
	sckobj.setblocking(False)
	global running
	while running:
		try:
			conn, addr = sckobj.accept()
			LOGGER.info(f"Connected by {addr}")
			th = threading.Thread(target=handler, args=(conn,addr))
			th.start()
		except BlockingIOError:
			pass
		except Exception as e:
			print(f"Error accepting conn: {e}")
		time.sleep(0.1)

def deleteDiscons():
	L = connections['viewers']
	tLen = len(L)
	for i in range(tLen):
		ind = tLen - i - 1
		if (isDisconnected(L[ind])):
			LOGGER.info("disposed off a wasted viewer conn")
			conn = connections['viewers'].pop(ind)
			cleanup(conn)

	D = connections['messengers']
	for name in list(D.keys())[:]:
		if isDisconnected( connections['messengers'][name] ):
			LOGGER.info("disposed off a wasted msngr conn")
			conn = connections['messengers'][name]
			cleanup(conn)
			del connections['messengers'][name]
			messageQ.put( (name, f'{name} has left the chat') )
	



def run():
	global running
	LOGGER.info(f"Starting the chat room on port {PORT}")
	print("Server started, press Ctr+C to exit")
	threading.Thread(target=newConnHandler).start()

	try:
		while running:
			deleteDiscons()
			checkForNewMessages()
			sendMessages()
			time.sleep(0.1)
	except KeyboardInterrupt:
		running = False
		for conn in connections['viewers']:
			cleanup(conn)
		for conn in connections['messengers'].values():
			cleanup(conn)
	finally:
		sckobj.close()


if __name__ == '__main__':
	run()

