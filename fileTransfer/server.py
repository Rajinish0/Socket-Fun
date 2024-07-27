from utils import *
from socket import *
import threading, time, hashlib
from block import Block
from packet import *
from global_constants import *
from threading import Lock
import codes, zlib
import logging, os
import queue


HOST = "" # localhost
PORT = 50008
running = True

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S')

LOGGER = logging.getLogger(os.path.basename(__file__))


messageQ = queue.Queue()

sckobj = socket(AF_INET, SOCK_DGRAM) #udp/ip
sckobj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sckobj.bind((HOST, PORT))
#sckobj.listen(5)

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


class States:
	WAITING_FOR_REQF 	= 1
	READY_FOR_TRANSFER  = 2
	WAITING_FOR_ACK 	= 3
	WAITING_FOR_REQB	= 4
	GREAT_SUCCESS		= 5


def checkMsgs():
	#print('chking')
	sckobj.setblocking(False)
	try:
	#	print("CHEKING")
		data, address =  sckobj.recvfrom(CHUNK_SZ)
		#LOGGER.info(f"RECEIVED MSG {data} from {address}")
		messageQ.put( (Packet.fromBytes(data), address) )
	except BlockingIOError:
		pass
		

def start():
	running = True  ## this is local now!!	
	curState = States.WAITING_FOR_REQF
	fname = None
	blocks = dict()
	receiver = None

	def resetState():
		nonlocal receiver, fname, blocks, curState
		curState = States.WAITING_FOR_REQF
		fname = None
		receiver = None
		blocks = dict()
	#LOGGER.info(f"Handling connection request from {addr}")

	while running:
		#print('calling check')
		checkMsgs()
		message = messageQ.get() if not messageQ.empty() else None
		isBye = (message is not None and message[0].isBye()) 
		if isBye:
			resetState()
			LOGGER.info("Received bye waiting for next client")

		match curState:
			case States.WAITING_FOR_REQF:
				#LOGGER.info("NOW HERE")
				isREQF = (message is not None and message[0].isREQF())
				if not isREQF:
				#	LOGGER.info('no REQF going back')
					continue
				LOGGER.info("got reqf data")

				#data = getAllAvailableData(conn)
				#LOGGER.info("got the data")
				#packet = Packet.fromBytes(data)
				packet, addr = message
				LOGGER.info(f"Recieved {packet} from {addr}")
				pkt = REQFPacket(packet)
				fname = pkt.fileName
				pktToSend = AckPacket()
				if (os.path.exists(fname)):
					pktToSend.message = fname
					curState = States.READY_FOR_TRANSFER
					receiver = addr
					print(receiver)
				LOGGER.info(f"Sending {packet} to {addr}")
				sckobj.sendto(pktToSend.toBytes(), addr)
			
			##doing uncompressed for now
			case States.READY_FOR_TRANSFER:
				pkt = InfoPacket()
				fileData = open(fname, 'rb').read()
				pkt.checkSum = hashlib.md5(fileData).digest()
				fileData = zlib.compress(fileData)
				pkt.fileSize = len(fileData)
				pkt.maxBlockSize = MAX_BLOCK_SIZE	
				for i in range(0, len(fileData), MAX_BLOCK_SIZE):
					id_ = i // MAX_BLOCK_SIZE
					blocks[id_] = Block(id_, fileData[i:i+MAX_BLOCK_SIZE]) 
				pkt.blockCount = len(blocks)
				
				LOGGER.info(
					f'''check sum {pkt.checkSum}\n
					  fileSize {pkt.fileSize}\n
					  mBsz {pkt.maxBlockSize}\n
					  bcount {pkt.blockCount}'''
				)

				sckobj.sendto(pkt.toBytes(), receiver)
				curState = States.WAITING_FOR_ACK

			case States.WAITING_FOR_ACK:
				isAck = (message is not None and message[0].isAck())
				if (not isAck):
					continue
				#data = getAllAvailableData(conn)
				#packet = Packet.fromBytes(data)
				packet = message[0]
				LOGGER.info(f"Receveid {packet}")
				#if (not packet.isAck()): 
			#		resetState()
			#		continue
				curState = States.WAITING_FOR_REQB
				LOGGER.info("RECEVEID ACK changing to waiting for REQB")

			case States.WAITING_FOR_REQB:
				isREQB = (message is not None and message[0].isREQB())
				if (not isREQB):
					continue
				#data = getAllAvailableData(conn)
				packet, addr = message
				#packet = Packet.fromBytes(data)
				#LOGGER.info(f"Received {packet}")
				if (not packet.isREQB()):
					resetState()
					continue
				packet = REQBPacket(packet)
				number = packet.number
				if (number not in blocks):
					LOGGER.info("received unknown block id")
					resetState()
				pkt = SendPacket()
				pkt.payload = blocks[number].toBytes()
				#print(f"Sending send {pkt}")
				sckobj.sendto(pkt.toBytes(), addr)

		time.sleep(0.1)

	if receiver != None:
		packet = Packet(codes.BYE)
		sckobj.sendto(packet.toBytes(), receiver)



def run():
	global running
	LOGGER.info(f"Starting the chat room on port {PORT}")
	print("Server started, press Ctr+C to exit")
	#threading.Thread(target=newConnHandler).start()

	try:
		start()
	except KeyboardInterrupt:
		running = False
		pass
	finally:
		sckobj.close()


if __name__ == '__main__':
	run()

