from utils import *
from socket import *
import sys, pprint, threading
import codes, time, os

# ideally exit or quit should be typed to exit this
# ctrl + c leaves a trail of error msgs, but it works

HOST = "localhost"
PORT = 50008
CHUNK_SZ = 1024
running = True

def sendData(conn, data):
	msgLen = len(data)
	if msgLen == 0 or msgLen > 100: return
	fullMsg = f'{str(msgLen).zfill(2)}{data}'
	conn.sendall(fullMsg.encode('utf-8'))

def parseData(conn, tLen):
	data = b''
	while (tLen > 0):
		d = conn.recv( min(tLen, CHUNK_SZ) )
		if (not d): break
		data += d
		tLen -= len(d)
	return data

def recvAndPrintMessage(conn, msgLen):
	msg = parseData(conn, int(msgLen))
	print('\r' + msg.decode('utf-8'), end="")
	print("\n>", end="")
	sys.stdout.flush()

def connectToServer(name):
	try:
		sckobj = socket(AF_INET, SOCK_STREAM) ## use tcp/ip
		sckobj.connect((HOST, PORT))

		sckobj.send(
			codes.NAME
		)
		sendData(sckobj, name)

		return sckobj
	except Exception as e:
		print("ERROR WHILE CONNECTING TO SERVER: ", e)
		return None



def sendMessages(sckobj):
	global running
	while running:
		msg = input(f">")
		
		if isDisconnected(sckobj):
			print("SERVER DISCONNECTED")
			running = False
			return

		if (msg.lower() == 'quit' or msg.lower() == 'exit'):
			print('exiting')
			running = False
		elif len(msg) > 0:
			sendData(sckobj, msg)

def getMessages(conn):
	global running
	while running:
		try:
			msgLen = conn.recv(2)
			if (len(msgLen) == 0):
				running = False
				return
			recvAndPrintMessage(conn, msgLen)
		except BlockingIOError:
			pass
		except error:
			print("SERVER DISCONNECTED")
			running = False
		running = not isDisconnected(conn)
		time.sleep(0.1)

def initMessageReceiver(conn):
	print("INITIALIZING LISTENER")
	threading.Thread(target=getMessages, args=(conn,)).start()


def run():
	#os.system('cls' if os.name == 'nt' else 'clear')
	sckobj = connectToServer(sys.argv[1])
	time.sleep(0.5)
	if sckobj is None or isDisconnected(sckobj):
		print("Couldn't connect to the server, name probably already taken")
		return
	else:
		try:
			initMessageReceiver(sckobj)
			sendMessages(sckobj)
		finally:
			sckobj.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('usage ./message.py [name]')
	else:
		run()
