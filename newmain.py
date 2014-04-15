from pygame import *
init()

import sys
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1,1"

import numpy as np
from random import randrange

class Camera:
	def __init__(self, image):
		self.x, self.y = 0, 0
		self.max_x = image.get_width()//1280 + 1
		self.max_y = image.get_height()//1024 + 1

class Map:
	def __init__(self, name):
		map_name = name

		self.image = image.load(map_name + ".png")

		raw_collision = [list(map(int, list(line))) for line in open(str(mapname) + ".txt", "r").readlines()]
		self.collision = np.array([[rawcollision[x*16:x*16+16][y*20:y*20+20] for y in range(ycam_max)] for x in range(xcam_max)])

		self.camera = Camera(self.image)

	def collide(self, location):
		


class Player:
	def __init__(self, location, direction):
		self.x, self.y = location
		self.direction = direction

	def teleport(self, location, direction):
		self.x, self.y = location
		self.direction = direction

	def location(self):
		return (self.x, self.y)
	
class Game:
	def __init__(self):
		screen = display.set_mode((1280,1024))
		world = Map("testmap1")
		player = Player((0, 0))

	def run(self, framecap, debug=0):
		pass

	def screenslide(self, direction):
	    speed = 32
	    if direction == "R":
	        for step in range(self.world.x * 1280, (self.world.x+1) * 1280, speed):
	            self.screen.fill((0, 0, 0))
	            self.screen.blit(world, (0, 0), area=(step, self.world.y * 1024, 1280, 1024))
	            self.player.x -= 30.5
	            self.screen.blit(self.current_sprite(), (self.player.x, self.player.y))
	            display.flip()
	    elif direction == "L":
	        for step in range((self.world.x-1) * 1280, self.world.x * 1280, speed)[::-1]:
	            self.screen.fill((0, 0, 0))
	            self.screen.blit(world, (0, 0), area=(step, self.world.y * 1024, 1280, 1024))
	            self.player.x += 30.5
	            self.screen.blit(self.current_sprite(), (self.player.x, self.player.y))
	            display.flip()
	    elif direction == "D":
	        for step in range(self.world.y * 1024, (self.world.y+1) * 1024, speed):
	            self.screen.fill((0, 0, 0))
	            self.screen.blit(world, (0, 0), area=(self.world.x * 1280, step, 1280, 1024))
	            self.player.y -= 30
	            self.screen.blit(self.current_sprite(), (self.player.x, self.player.y))
	            display.flip()
	    elif direction == "U":
	        for step in range((self.world.y-1) * 1024, self.world.y * 1024, speed)[::-1]:
	            self.screen.fill((0, 0, 0))
	            self.screen.blit(world, (0, 0), area=(self.world.x * 1280, step, 1280, 1024))
	            self.player.y += 30
	            self.screen.blit(self.current_sprite(), (self.player.x, self.player.y))
	            display.flip()




def main():
	Game()

if __name__ == '__main__':
	main()