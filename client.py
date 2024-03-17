from socket import *
import sys, pprint, threading
from codes import Codes
import pygame

HOST = "localhost"
PORT = 50007
BLANK = '-'
ME = 'X'
OP = 'O'
W, H = 810, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
NUM_BOXES = 3

def connectToServer():
	global ME, OP
	sckobj = socket(AF_INET, SOCK_STREAM) ## use tcp/ip
	sckobj.connect((HOST, PORT))
	msg = b'Hello network'
	sckobj.send(msg)
	data = sckobj.recv(1024)
	print(f"Received: [{data}]")

	data = sckobj.recv(2).decode()
	print(f"Recevied: [{data}]")
	ME, OP = data[0], data[1]
	return sckobj

def drawText(screen, text, x, y, size=30, color=WHITE, font_type="Comic Sans MS"):
	text = str(text)
	font = pygame.font.SysFont(font_type, size)
	surface = font.render(text, True, color)
	text_width, text_height = font.size(text)
	screen.blit(surface, (x-text_width/2, y-text_height/2))

def ScreenCoordToIdx(x, y, bw, bh):
	j = x // bw
	i = y // bh 
	return j + i*NUM_BOXES





class WaitingScreen:
	def __init__(self, text, fontSize = 50, color=WHITE):
		self.fontSize = fontSize
		self.text = text
		self.col = color

	def draw(self, display):
		drawText(display, self.text, W//2, H//2, size=self.fontSize)

def printBoard(board):
	pprint.pprint(board)

class Game:
	def __init__(self):
		self.board = [BLANK for j in range(9)]
		self.display = pygame.display.set_mode((W, H))
		self.waitingScreen = WaitingScreen("Waiting for other player...")
		self._start = False
		self.boxWidth = W // NUM_BOXES
		self.boxHeight = (H-30) // NUM_BOXES
		self.running = True
		self.myTurn = False
		self.mouseDown = False
		self.gameEnd = False
		self.winner = None
		self.sckobj = connectToServer()
		self.initCheckForStartThread()

	def checkForStart(self):
		if self.sckobj.recv(1) != Codes.BEGIN_CODE:
			print("received erroneous code, exiting!!")
			sys.exit(1)
		else:
			self._start = True
			self.initHandler()
			print("Starting the game!!")

	def draw(self):
		if not self.gameEnd:
			t = "IT'S YOUR TURN" if self.myTurn else "IT'S NOT YOUR TURN"
		else:
			if self.winner is None:
				t = "Game Tied"
			elif self.winner == ME:
				t = "You won!"
			else:
				t = "You lost!"
		drawText(self.display, t, W//2, 15, 30)
		for y in range(30, H, self.boxHeight):
			for x in range(0, W, self.boxWidth):
				pygame.draw.rect(self.display, WHITE, 
				(x, y, self.boxWidth, self.boxHeight), 1)

				idx = ScreenCoordToIdx(x, y, self.boxWidth, self.boxHeight)

				if self.board[idx] == ME:
					drawText(self.display, ME, x + self.boxWidth//2, y + self.boxHeight//2, color=GREEN)
				elif self.board[idx] == OP:
					drawText(self.display, OP, x + self.boxWidth//2, y + self.boxHeight//2, color=RED)

	def handleMsgs(self):
		while True:
			match (self.sckobj.recv(1)):
				case Codes.DATA_UPDATE:
					d = int(self.sckobj.recv(1).decode())
					self.board[d] = OP
				case Codes.TURN_CODE:
					self.myTurn = True
				case Codes.TURN_OFF:
					print("Other player disconnected")
					self.running = False
				case _:
					print('ERROR CODE, exiting')
					self.running = False
		# self.sckobj.close()

	def checkRows(self):
		for i in range(NUM_BOXES):
			if all(self.board[j + i*NUM_BOXES] == self.board[i*NUM_BOXES] and 
		  		   self.board[j + i*NUM_BOXES] != BLANK for j in range(NUM_BOXES)):
				self.winner = self.board[i*NUM_BOXES]
				return True
		return False

	def checkCols(self):
		for j in range(NUM_BOXES):
			if all(self.board[j + i*NUM_BOXES] == self.board[j] and 
		  		   self.board[j + i*NUM_BOXES] != BLANK for i in range(NUM_BOXES)):
				self.winner = self.board[j]
				return True
		return False

	def checkDiags(self):
		if all(self.board[i + NUM_BOXES*i] == self.board[0] and 
		 	   self.board[i + NUM_BOXES*i] != BLANK for i in range(NUM_BOXES)):
			self.winner = self.board[0]
			return True
		
		if all(self.board[(NUM_BOXES-i-1) + NUM_BOXES*i] == self.board[NUM_BOXES-1] and 
		 	   self.board[(NUM_BOXES-i-1) + NUM_BOXES*i] != BLANK for i in range(NUM_BOXES)):
			self.winner = self.board[NUM_BOXES-1]
			return True
		return False 



	def checkForGameEnd(self):
		if (self.gameEnd     or
		   self.checkRows()  or
	  	   self.checkCols()  or 
		   self.checkDiags() or
		  (BLANK not in self.board)):
			self.gameEnd = True

	def initHandler(self):
		th = threading.Thread(target=Game.handleMsgs, args=(self,))
		th.daemon = True
		th.start()

	def initCheckForStartThread(self):
		th = threading.Thread(target=Game.checkForStart, args=(self,))
		th.daemon = True 
		th.start()

	def run(self):
		while self.running:
			self.display.fill(BLACK)
			if not self._start:
				self.waitingScreen.draw(self.display)
				# print("DRAWING WAITING SCREEN")
			else:
				self.draw()
			pygame.display.flip()
			self.pollEvents()
			self.handleMouse()
			self.checkForGameEnd()

	def handleMouse(self):
		if self.myTurn and self.mouseDown and not self.gameEnd:
			(mx, my) = pygame.mouse.get_pos()
			idx = ScreenCoordToIdx(mx, my, self.boxWidth, self.boxHeight)
			if self.board[idx] == BLANK:
				self.board[idx] = ME
				self.myTurn = False
				self.sckobj.send(str(idx).encode())
	
	def pollEvents(self):
		self.mouseDown = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False 

			if event.type == pygame.MOUSEBUTTONDOWN:
				self.mouseDown = True
	
	def __del__(self):
		self.sckobj.close()


if __name__ == '__main__':
	pygame.init()
	g = Game()
	g.run()


# while True:
# 	print("Waiting for turn")
# 	match (sckobj.recv(1)):
# 		case Codes.DATA_UPDATE:
# 			d = int(sckobj.recv(1).decode())
# 			board[d] = OP
# 			printBoard()
# 		case Codes.TURN_CODE:
# 			inp = input("Enter a number: ")
# 			board[int(inp)] = ME
# 			printBoard()
# 			sckobj.send(inp.encode())
# 		case _:
# 			print('ERROR CODE, exiting')
# 			sys.exit(1)
# sckobj.close()
