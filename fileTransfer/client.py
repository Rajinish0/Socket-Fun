from utils import *
from socket import *
from block import Block
from packet import *
from global_constants import *
import sys, pprint, threading, hashlib
import codes, time, os, queue, zlib

HOST = "localhost"
PORT = 50008
#CHUNK_SZ = 1024
running = True

def waitForData(sckobj, interval=0.1, timeout=5):
	startTime = time.time()
	while time.time() < startTime + timeout:
			if (dataIsAvailable(sckobj)):
				return True
			time.sleep(interval)
	return False

def requestBlocks(conn, addr, fileSize, maxBlockSize, blockCount):
	print("Requesting..", end='\r')
	blocks = dict()
	blockQ = queue.Queue()

	for i in range(blockCount):
		blockQ.put(i)
	
	while not blockQ.empty():
		reqNum = blockQ.get()
		packet = REQBPacket()
		packet.number = reqNum

#		print(f"SENT REQB FOR BLOCK {reqNum}")
		conn.sendto(packet.toBytes(), addr)

#		print("WAIITING FOR DATA")
		good = waitForData(conn)
		if (not good):
			blockQ.put(reqNum)
			continue

		data, _ = conn.recvfrom(CHUNK_SZ)
		packet = Packet.fromBytes(data)
		if (not packet.isSend()):
#			print("Did not get send, will requeue block req")
			blockQ.put(reqNum)
			continue
		packet = SendPacket(packet)
#		print(f'received send {packet}')
		blocks[reqNum] = packet.block
		print(f'Dowloaded {round( (len(blocks)/blockCount) * 100, 2) }%', end='\r')
	
	print('')
	return blocks

def setUpPath(path):
	direc = os.path.dirname(path)
	if (not os.path.exists(direc)):
		os.mkdir(direc)

def connectToServer(fname, pathToSave):
	sckobj = socket(AF_INET, SOCK_DGRAM) ## use udp/ip
	addr = (HOST, PORT)
	try:
		#sckobj.connect((HOST, PORT))

		setUpPath(pathToSave)
		
		print(f"Requesting for file {fname}")
		packet = REQFPacket()
		packet.fileName = fname

		print(f'Sending {packet}')
		sckobj.sendto(
			packet.toBytes(), addr
		)
		
		#print("Sent the packet, quiting")
			
		waitForData(sckobj)
		
		
		#if isDisconnected(sckobj):
		#	print("FAILED")
		#	raise Exception("server discon")
		
		#data = getAllAvailableData(sckobj)
		data, _ = sckobj.recvfrom(CHUNK_SZ)
		packet = Packet.fromBytes(data)
		print(f"packet is {packet}")
		if (not packet.isAck()):
			raise Exception("did not recv ack")

		packet = AckPacket(packet)

		print(f"Received {packet}")

		if (packet.message != fname):
			raise Exception("Server does not have the file or didn't send ACK")
		
		waitForData(sckobj)

		#if (isDisconnected(sckobj)):
		#	raise Exception("server discon")

		data, _ = sckobj.recvfrom(CHUNK_SZ)
		packet = Packet.fromBytes(data)
		
		print(f'Received {packet}')

		if (not packet.isInfo()):
			raise Exception("Did not get expected info packet")

		packet = InfoPacket(packet)
		checkSum = packet.checkSum
		fileSize = packet.fileSize
		maxBlockSize = packet.maxBlockSize
		blockCount = packet.blockCount
		
		print("SENDING ACK")
		packet = AckPacket()
		sckobj.sendto(packet.toBytes(), addr)
		
		print("REQUESTING BLOCKS")
		blocks = requestBlocks(sckobj, addr, fileSize, maxBlockSize, blockCount)
		print("GOT THE BLOCKS!!")
		data = b''
		for i in range(blockCount):
			data += blocks[i].data
		data = zlib.decompress(data)
		#data = b''.join(map(lambda block: block.data, blocks.values()))
		vrfy = hashlib.md5(data).digest()
		if (vrfy != checkSum):
			raise Exception("Couldnt transfer data was corrupted")

		print("Checksum verified")

		print("Writing file")
		with open(pathToSave, 'wb') as f:
			f.write(data)

		print("Successfully downloaded file")
		
		#assert False

		return sckobj
	except Exception as e:
		print("ERROR WHILE CONNECTING TO SERVER: ", e)
		return None
	
	finally:
		sckobj.sendto(
			Packet(codes.BYE).toBytes(),
			addr
		)



def run():
	#os.system('cls' if os.name == 'nt' else 'clear')
	sckobj = connectToServer(sys.argv[1], sys.argv[2])
	if (sckobj):
		sckobj.close()

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('usage ./message.py [fname] [path-to-save]')
	else:
		run()
