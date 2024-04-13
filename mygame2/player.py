import pygame

class Player:
	def __init__(self, pos):
		self.x, self.y = pos

	def draw(self, display):
		pygame.draw.rect(
			display, (255, 0, 0), (self.x, self.y, 100, 100), 1
			)

	def move(self, ds):
		(dx, dy) = ds
		self.x += dx
		self.y += dy

	def drawForeigners(self, display, foreigners):
		for foreigner in foreigners.values():
			foreigner.draw(display)