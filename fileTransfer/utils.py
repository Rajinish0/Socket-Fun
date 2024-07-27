import socket, codes
from global_constants import *

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



def getAllAvailableData(conn):
    conn.setblocking(False)
    data = b''
    try:
        while ( d := conn.recv(CHUNK_SZ) ):
            data += d
    except BlockingIOError:
        pass
    finally:
        conn.setblocking(True)

    return data

# FOR UDP
def dataIsAvailable(conn):
	conn.setblocking(False)
	try:
		data, _ = conn.recvfrom(1, socket.MSG_PEEK)
		return True
	except BlockingIOError:
		return False
	finally:
		conn.setblocking(True)
