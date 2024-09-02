import pygame

GRID_SIZE = [700//25, 700//25]

class Sprite(pygame.sprite.Sprite): 
	def __init__(self,dimentions, pos, image): 
		super().__init__() 
		self.image = image
		self.image = pygame.transform.scale(self.image, dimentions)
		self.rect = self.image.get_rect(center = pos)

class centipede():
	def __init__(self, pos, direction_x, direction_y, length, speed, head, body):
		self.pos = list(pos)
		self.direction_x = direction_x
		self.direction_y = direction_y
		self.length = length
		self.speed = speed
		self.construction = []
		for i in range(length):
			if i == 0:
				self.construction.append(boddypart([self.pos[0] - i*GRID_SIZE[0],self.pos[1]], Sprite(GRID_SIZE, self.pos, head), direction_x, direction_y))
			else:
				self.construction.append(boddypart([self.pos[0] - i*GRID_SIZE[0],self.pos[1]], Sprite(GRID_SIZE, self.pos, body), direction_x, direction_y))
		
class boddypart():
	def __init__(self, pos, sprite, direction_x, direction_y):
		self.pos = list(pos)
		self.sprite = sprite
		self.direction_x = direction_x
		self.direction_y = direction_y

class mushroom():
	def __init__(self, pos, sprite):
		self.pos = list(pos)
		self.lifes = 4
		self.sprite = Sprite(GRID_SIZE, self.pos, sprite)
		
		
	
    

		
        
    