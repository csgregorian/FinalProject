from pygame import *
import sys
import os
import numpy as np
from random import randrange

os.environ['SDL_VIDEO_WINDOW_POS'] = "1,1"

def screenslide(direction):
    global self
    speed = 32
    if direction == "R":
        for step in range(xcamera * 1280, (xcamera+1) * 1280, speed):
            screen.fill((0, 0, 0))
            screen.blit(world, (0, 0), area=(step, ycamera * 1024, 1280, 1024))
            self.x -= 30.5
            screen.blit(self.current_sprite(), (self.x, self.y))
            display.flip()
    elif direction == "L":
        for step in range((xcamera-1) * 1280, xcamera * 1280, speed)[::-1]:
            screen.fill((0, 0, 0))
            screen.blit(world, (0, 0), area=(step, ycamera * 1024, 1280, 1024))
            self.x += 30.5
            screen.blit(self.current_sprite(), (self.x, self.y))
            display.flip()
    elif direction == "D":
        for step in range(ycamera * 1024, (ycamera+1) * 1024, speed):
            screen.fill((0, 0, 0))
            screen.blit(world, (0, 0), area=(xcamera * 1280, step, 1280, 1024))
            self.y -= 30
            screen.blit(self.current_sprite(), (self.x, self.y))
            display.flip()
    elif direction == "U":
        for step in range((ycamera-1) * 1024, ycamera * 1024, speed)[::-1]:
            screen.fill((0, 0, 0))
            screen.blit(world, (0, 0), area=(xcamera * 1280, step, 1280, 1024))
            self.y += 30
            screen.blit(self.current_sprite(), (self.x, self.y))
            display.flip()

def collide(x, y):
    try:
        return collision[int(ycamera)][int(xcamera)][int(y//64)][int(x//64)] == 1
    except IndexError:
        return False
    except TypeError:
        return False

class Player:
    def __init__(self):
        self.x = 64*4
        self.y = 64*3
        self.dir = "R"
        self.sprite = {x: (transform.scale(image.load(x+"1.png"), (64, 64)),
                        transform.scale(image.load(x+"2.png"), (64, 64))) for x in ["R", "L", "D", "U"]}
        self.speed = 8
        self.frame = 0
    def current_sprite(self):
        return self.sprite[self.dir][self.frame]
    def update(self):
        global xcamera, ycamera
        self.frame = frametracker1%20//10
        if self.x > 1216 and xcamera < 7:
            screenslide("R")
            xcamera += 1
        elif self.x < 0 and xcamera > 0:
            screenslide("L")
            xcamera -= 1
        elif self.y > 960 and ycamera < 7:
            screenslide("D")
            ycamera += 1
        elif self.y < 0 and ycamera > 0:
            screenslide("U")
            ycamera -= 1
    def keys(self):
        if key.get_pressed()[K_RIGHT]:
            self.dir = "R"
            if not collide(self.x+64, self.y+16) and not collide(self.x+64, self.y+48):
                self.x += self.speed
                self.update()
        elif key.get_pressed()[K_LEFT]:
            self.dir = "L"
            if not collide(self.x+16, self.y+16) and not collide(self.x, self.y+48):
                self.x -= self.speed
                self.update()
        if key.get_pressed()[K_DOWN]:
            self.dir = "D"
            if not collide(self.x+16, self.y+64) and not collide(self.x+48, self.y+64):
                self.y += self.speed
                self.update()
        elif key.get_pressed()[K_UP]:
            self.dir = "U"
            if not collide(self.x+16, self.y) and not collide(self.x+48, self.y):
                self.y -= self.speed
                self.update()
        if key.get_pressed()[K_x]:
            self.attack()
    def attack(self):
        pass
    def centre_tile(self):
        x = self.x + 32
        y = self.y + 32
        if self.dir == "R":
            return ((x-32) // 64, y // 64)
        elif self.dir == "L":
            return ((x+32) // 64, y // 64)
        elif self.dir == "D":
            return (x // 64, (y-32) // 64)
        elif self.dir == "U":
            return (x // 64, (y+32) // 64)

class Enemy:
	def __init__(self):
		self.x = 64 * randrange(20)
		self.y = 64 * randrange(16)
		self.dir = "D"


#Map is 20x16 tiles, tiles are 16x16 units, units are 4x4 pixels
init()
screen = display.set_mode((1280,1024))
world = image.load("testmap1.png")
xcamera, ycamera = 0, 0
xcam_max, ycam_max = world.get_width()//1280 + 1, 1+world.get_height()//1024 + 1

rawcollision = [list(map(int, list(x))) for x in open("testmap1.txt", "r").read().strip().split()]

collision = np.array([[rawcollision[d*16:d*16+16][c*20:c*20+20] for c in range(ycam_max)] for d in range(xcam_max)])


running = True

self = Player()
frametracker1 = 0
fpsTrack = time.Clock()
segoeui = font.SysFont("Arial", 48)

class Game:
	def __init__(self):
		self.link = Player()
		self.screen = 

	def play(self):
		while self.running:
		    for ev in event.get():
		        if ev.type == QUIT:
		            self.running = False
		    self.link.keys()


		    screen.blit(world, (0, 0), area=(xcamera * 1280, ycamera * 1024, 1280, 1024))

		    #Shows collision tiles
		    # for x in range(20):
		    #     for y in range(16):
		    #         if collide(x*64, y*64):
		    #             screen.fill((255, 255, 255), (64*x, 64*y, 64, 64))

		    screen.blit(self.link.current_sprite(), (self.link.x, self.link.y))
		    fpsTrack.tick(30)
		    if fpsTrack.get_time() > 0:
		        screen.blit(segoeui.render(str(1000//fpsTrack.get_time()), True, (255, 255, 255)), (0, 0))

		    display.flip()
		    frametracker1 = (frametracker1 + 1) % 300

		quit()
		sys.exit()

Game().play()