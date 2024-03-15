from socket import *
import threading, time
from codes import Codes


HOST = ""
PORT = 50007


sckobj = socket(AF_INET, SOCK_STREAM)
sckobj.bind((HOST, PORT))
sckobj.listen(2)
threads = []
players = []
curPlayer = 0

def now():
	return time.ctime(time.time())

def handler(conn, addr):
	global curPlayer
	data = conn.recv(1024)
	if not data: conn.close(); return
	print(f"Received [{data}] from {addr} at {now()}")
	conn.send(b'You have successfully connected to the server')

	while len(players) != 2:
		time.sleep(0.1)	 ## wait until all players have connected
	
	time.sleep(0.01) ## synchronize both handlers
	conn.send(Codes.BEGIN_CODE)

	while True:
		while conn != players[curPlayer]:
			time.sleep(0.1) ## wait for turn
		conn.send(Codes.TURN_CODE)
		k = conn.recv(1)
		curPlayer = not curPlayer
		players[curPlayer].send(Codes.DATA_UPDATE)
		players[curPlayer].send(k)

	conn.close()

def run():
	while len(players) != 2:
		conn, addr = sckobj.accept()
		print(f"Connected by {addr}")
		th = threading.Thread(target=handler, args=(conn,addr))
		threads.append(th)
		players.append(conn)
		th.start()
	for thread in threads:
		thread.join()


if __name__ == '__main__':
	run()
