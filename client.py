from socket import *
import sys, pprint
from codes import Codes
import pygame

HOST = "localhost"
PORT = 50007
BLANK = '-'
ME = 'X'
OP = 'O'

board = [BLANK for j in range(9)]

def printBoard():
	pprint.pprint(board)
msg = b'Hello network'

sckobj = socket(AF_INET, SOCK_STREAM) ## use tcp/ip
sckobj.connect((HOST, PORT))


sckobj.send(msg)
data = sckobj.recv(1024)
print(f"Received: [{data}]")

print("Waiting for other players...")
if sckobj.recv(1) != Codes.BEGIN_CODE:
	print("received erronous code, exiting!!")
	sys.exit(1)
	
print('Starting the game!!')
while True:
	print("Waiting for turn")
	match (sckobj.recv(1)):
		case Codes.DATA_UPDATE:
			d = int(sckobj.recv(1).decode())
			board[d] = OP
			printBoard()
		case Codes.TURN_CODE:
			inp = input("Enter a number: ")
			board[int(inp)] = ME
			printBoard()
			sckobj.send(inp.encode())
		case _:
			print('ERROR CODE, exiting')
			sys.exit(1)
sckobj.close()
