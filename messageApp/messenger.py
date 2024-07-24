from utils import *
from socket import *
import sys, pprint, threading
import codes, time



HOST = "localhost"
PORT = 50008
running = True

def sendData(conn, data):
	msgLen = len(data)
	if msgLen == 0 or msgLen > 100: return
	fullMsg = f'{str(msgLen).zfill(2)}{data}'
	conn.sendall(fullMsg.encode('utf-8'))

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
		msg = input(f"name>")
		
		if isDisconnected(sckobj):
			print("SERVER DISCONNECTED")
			running = False
			return

		if (msg.lower() == 'quit' or msg.lower() == 'exit'):
			print('exiting')
			running = False
		elif len(msg) > 0:
			sendData(sckobj, msg)


def run():
	sckobj = connectToServer(sys.argv[1])
	time.sleep(0.5)
	if sckobj is None or isDisconnected(sckobj):
		print("Couldn't connect to the server, name probably already taken")
		return
	else:
		try:
			sendMessages(sckobj)
		finally:
			sckobj.close()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('usage ./message.py [name]')
	else:
		run()
