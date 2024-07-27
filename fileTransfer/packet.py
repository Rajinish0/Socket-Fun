import codes, struct
from global_constants import *
from block import Block

'''
I'm using only 1 byte for packetType might change that later
and the biggest packet is info packet
which is 16 + 4 + 4 + 4 = 28 bytes 

so the biggest packet size is 29 bytes in total

TO DO:
	packets should either have a fixed size (with padding)
	or they should have info about their size
'''

class Packet:
	def __init__(self, packetType):
		self.packetType = packetType
		self.payload = b''
	
	def isAck(self):
		return (self.packetType == codes.ACK)
	
	def isBye(self):
		return (self.packetType == codes.BYE)
	
	def isREQF(self):
		return (self.packetType == codes.REQF)

	def isREQB(self):
		return (self.packetType == codes.REQB)
	
	def isInfo(self):
		return (self.packetType == codes.INFO)
	
	def isSend(self):
		return (self.packetType == codes.SEND)

	def toBytes(self):
		return (
			self.packetType +
			self.payload
		)
	
	def __repr__(self):
		return f'''\
			[Packet:\n
			\tType={self.packetType}\n
			\tpayloadSize={len(self.payload)}\n
			\tpayload={self.payload}]'''

	__str__ = __repr__

	@classmethod
	def fromBytes(cls, byteString):
		assert type(byteString) is bytes
		type_ = byteString[:1] # this stops it from converting it to number
		pckt = cls(
			type_
		)
		pckt.payload = byteString[1:]
		return pckt


class AckPacket(Packet):
	def __init__(self, packet = None):
		super().__init__(codes.ACK)
		if (packet):
			self.payload = packet.payload
	
	@property
	def message(self):
		return self.payload.decode(ENCODING)
	
	@message.setter
	def message(self, value):
		self.payload = value.encode(ENCODING)

class REQFPacket(Packet):
	def __init__(self, packet = None):
		super().__init__(codes.REQF)
		if (packet):
			self.payload = packet.payload

	@property
	def fileName(self):
		return self.payload.decode(ENCODING)
	@fileName.setter
	def fileName(self, value : str):
		self.payload = value.encode(ENCODING)
		return value

class REQBPacket(Packet):
	formatString = 'I' # 4 byte unsigned integer

	def __init__(self, packet = None):
		super().__init__(codes.REQB)
		if (packet):
			self.payload = packet.payload

	@property
	def number(self):
		return struct.unpack(self.formatString, self.payload)[0]
	
	@number.setter
	def number(self, value : int):
		self.payload = struct.pack(self.formatString, value)


class InfoPacket(Packet):
	formatString = 'I'
	intSize = 4

	def __init__(self, packet = None):
		super().__init__(codes.INFO)
		if (packet):
			self.payload = packet.payload
		self.payload = [byte for byte in self.payload]
	
	@property
	def checkSum(self):
		return bytes(self.payload[:16])

	@checkSum.setter
	def checkSum(self, value):
		self.payload[:16] = list(value)

	@property
	def fileSize(self):
		return struct.unpack(self.formatString, bytes(self.payload[16:16+self.intSize]))[0]
	
	@fileSize.setter
	def fileSize(self, value):
		self.payload[16:16+self.intSize] = list(struct.pack(self.formatString, value))
	
	@property
	def maxBlockSize(self):	
		return struct.unpack(self.formatString, bytes(self.payload[16+self.intSize:16+self.intSize*2]))[0]

	@maxBlockSize.setter
	def maxBlockSize(self, value):
		self.payload[16+self.intSize:16+self.intSize*2] = list(struct.pack(self.formatString, value))

	@property
	def blockCount(self):
		return struct.unpack(self.formatString, bytes(self.payload[16+self.intSize*2:16+self.intSize*3]))[0]

	@blockCount.setter
	def blockCount(self, value):
		self.payload[16+self.intSize*2:16+self.intSize*3] = list(struct.pack(self.formatString, value))

	def toBytes(self):
		return (
			self.packetType +
			bytes(self.payload)
		)


	
class SendPacket(Packet):
	def __init__(self, packet = None):
		super().__init__(codes.SEND)
		if (packet):
			self.payload = packet.payload

	@property
	def block(self):
		return Block.fromBytes(self.payload)
	@block.setter
	def block(self, value : str):
		self.payload = value.encode(ENCODING)




