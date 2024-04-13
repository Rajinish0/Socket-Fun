CHUNK_SZ = 1024

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
	return data


