import pygame
from constants import W, H

def dist(pos1 : tuple, pos2 : tuple):
	x1, y1 = pos1
	x2, y2 = pos2
	return (x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2)


class Player:
	def __init__(self, pos, direc):
		self.pos = list(pos)
		self.dir = direc
		self.speed = 90
		self.w, self.h = 20, 20
		self.addCopy = False

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
	

	def draw(self, display):
		pygame.draw.rect(
			display, (255, 0, 0), (self.x, self.y, self.w, self.h), 1
			)

	def chdir(self, direc):
		self.dir = direc

	def checkForFood(self, foodPos):
		d = dist((self.x + self.w/2, self.y + self.h/2), foodPos) < 20
		# self.addCopy = d
		return d


	def update(self, dt):
		# if self.addCopy:
		# 	self.pos.append((self.pos[-1][:]))
		# for i in range(1, len(self.pos)):
		# 	self.pos[i] = self.pos[i-1][:]
		self.x += self.dir[0] * self.speed * dt
		self.y += self.dir[1] * self.speed * dt
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