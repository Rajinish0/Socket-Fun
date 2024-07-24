from utils import *
from socket import *
import sys, pprint, threading
import codes, time



HOST = "localhost"
PORT = 50008
CHUNK_SZ = 1024
running = True


def parseData(conn, tLen):
	data = b''
	while (tLen > 0):
		d = conn.recv( min(tLen, CHUNK_SZ) )
		if (not d): break
		data += d
		tLen -= len(d)
	return data

def recvAndPrintMessage(conn, msgLen):
	#msgLen = int(conn.recv(2))
	msg = parseData(conn, int(msgLen))
	print(msg.decode('utf-8'))

	#msgLen = len(data)
	#if msgLen == 0 or msgLen > 100: return
	#fullMsg = f'{str(msgLen).zfill(2)}{data}'
	#conn.sendall(fullMsg.encode('utf-8'))

def connectToServer():
	try:
		sckobj = socket(AF_INET, SOCK_STREAM) ## use tcp/ip
		sckobj.connect((HOST, PORT))
		

		sckobj.send(
			codes.VIEWER
		)
		time.sleep(0.5)
		sckobj.setblocking(False)
		
		welcomeMsg = sckobj.recv(1024)
		print(welcomeMsg.decode('utf-8'))
		
		sckobj.setblocking(True)

		return sckobj
	except Exception as e:
		print("ERROR WHILE CONNECTING TO SERVER: ", e)
		return None



def getMessages(sckobj):
	global running
	while running:
		try:
			msgLen = sckobj.recv(2)
			if (len(msgLen) == 0):
				running = False
				return
			recvAndPrintMessage(sckobj, msgLen)
		except BlockingIOError:
			pass
		except error: ## socket.error
			print("SERVER DISCONNECTED")
			running = False
		running = not isDisconnected(sckobj)
		time.sleep(0.1)

def run():
	print("Press ctrl+c to quit")
	sckobj = connectToServer()
	time.sleep(0.5)
	if sckobj is None or isDisconnected(sckobj):
		print("Couldn't connect to the server")
		return
	else:
		try:
			getMessages(sckobj)
		except KeyboardInterrupt:
			pass
		finally:
			print("Disconnecting...")
			sckobj.close()

if __name__ == '__main__':
	run()
