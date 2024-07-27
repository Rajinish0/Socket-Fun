import struct
class Block:
	formatString = "I"
	def __init__(self, number = 0, data=b""):
		self.number = number
		self.data = data
	
	def __repr__(self):
		return f'''
			[Block:\n
			\tNumber={self.number}\n
			\tSize={len(self.data)}\n,
			\tData={self.data}]'''

	__str__ = __repr__

	def toBytes(self):
		return (
			struct.pack(self.formatString, self.number) +
			self.data
		)

	@classmethod
	def fromBytes(cls, byteString):
		assert type(byteString) is bytes
		number = struct.unpack(cls.formatString, byteString[:4])[0]
		#number = int.from_bytes(byteString[:4])
		data = byteString[4:]
		return cls(number, data)
	
