import socket, codes

def isDisconnected(conn):
	conn.setblocking(False)
	try:
		data = conn.recv(1, socket.MSG_PEEK)
		if len(data) == 0:
			return True
		elif len(data) == 1 and data == codes.DISCONNECT:
			return True
		else:
			return False
	except BlockingIOError:
		#print("YES here")
		return False
	except socket.error:
		#print('ERROR OCCURED HERE')
		return True
	except Exception as e:
		print('Unknown Exception occured while checking for disconnection: ', e)
		return True
	finally:
		conn.setblocking(False)

