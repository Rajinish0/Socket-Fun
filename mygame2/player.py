import pygame
from constants import W, H

def dist(pos1 : tuple, pos2 : tuple):
	x1, y1 = pos1
	x2, y2 = pos2
	return (x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2)

def sign(val):
	if abs(val) < 1e-5: return 0 
	elif val > 0: return 1
	else: return -1

class Player:
	def __init__(self, body, direc):
		self.body = body
		# self.body = [list(pos)]
		self.dir = direc
		self.speed = 90
		self.w, self.h = 20, 20
		self.increaseSize = False

	@property
	def pos(self):
		return self.body[0]

	@property
	def x(self):
		return self.pos[0]

	@property
	def y(self):
		return self.pos[1]

	@x.setter
	def x(self, val):
		self.pos[0] = val 

	@y.setter
	def y(self, val):
		self.pos[1] = val

	@pos.setter
	def pos(self, val):
		self.body[0] = val

	

	def draw(self, display):
		for x, y in self.body:
			pygame.draw.rect(
				display, (255, 0, 0), (x, y, self.w, self.h), 1
				)

	def chdir(self, direc):
		self.dir = direc

	def checkForFood(self, foodPos):
		d = dist((self.x + self.w/2, self.y + self.h/2), foodPos) < 25
		return d

	def inc(self):
		self.increaseSize = True

	def update(self, dt):
		# if self.addCopy:
		self.body = [ [self.x + self.dir[0]*self.w, 
					  self.y + self.dir[1]*self.h] ] + self.body
		if not self.increaseSize:
			self.body.pop()
		else:
			self.increaseSize = False
		# else:
			# print('yipee')
		# else:
		# print(self.dir, self.w, self.x)
		# self.x += self.dir[0] * self.w
		# self.y += self.dir[1] * self.h
		# for i in range(1, len(self.pos)):
		# 	dx, dy = (self.pos[i-1][0] - self.pos[i][0], 
		# 			  self.pos[i-1][1] - self.pos[i][1])
		# 	dx, dy = sign(dx), sign(dy)
		# 	print(dx, dy)
		# 	self.pos[i] = [
		# 		self.pos[i-1][0] - dx*self.w,
		# 		self.pos[i-1][1] - dy*self.h
		# 	]
		if (self.x > W):
			self.x = -self.w
		elif (self.x + self.w) < 0:
			self.x = W
		elif (self.y > H):
			self.y = -self.h
		elif (self.y + self.h < 0):
			self.y = H
		# self.addCopy = False


	def drawForeigners(self, display, foreigners):
		for foreigner in foreigners.values():
			foreigner.draw(display)