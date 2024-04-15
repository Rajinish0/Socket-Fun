import pygame

class Player:
	def __init__(self, pos, direc):
		self.pos = list(pos)
		self.dir = direc
		self.speed = 50

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
			display, (255, 0, 0), (self.x, self.y, 100, 100), 1
			)

	def chdir(self, direc):
		self.dir = direc

	def update(self, dt):
		self.x += self.dir[0] * self.speed * dt
		self.y += self.dir[1] * self.speed * dt

		if (self.x > 800):
			self.x = -100
		elif (self.x + 100) < 0:
			self.x = 800
		elif (self.y > 600):
			self.y = -100
		elif (self.y + 100 < 0):
			self.y = 600

	def drawForeigners(self, display, foreigners):
		for foreigner in foreigners.values():
			foreigner.draw(display)