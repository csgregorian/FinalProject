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

        self.image = image.load(map_name + ".png").convert()

        self.camera = Camera(self.image)

        raw_collision = [list(map(int, list(line))) for line in open(str(map_name) + ".txt", "r").read().strip().split()]
        self.collision = np.array([[raw_collision[x*16:x*16+16][y*20:y*20+20] for y in range(self.camera.max_x)] for x in range(self.camera.max_y)])


    def collide(self, location):
        x, y = location
        try:
            return self.collision[int(self.camera.y)][int(self.camera.x)][int(y//64)][int(x//64)] == 1
        except IndexError:
            return False
        except TypeError:
            return False


class Player:
    def __init__(self, location, direction):
        self.x, self.y = location
        self.direction = direction
        self.state = "move"

        self.speed = 4


        self.sprite = {}
        for x in ["r", "l", "d", "u"]:
            self.sprite[x] = (transform.scale(image.load(x+"1.png"), (192, 192)),
                transform.scale(image.load(x+"2.png"), (192, 192)))

        self.frame = 0


    def teleport(self, location):
        self.x, self.y = location

    def location(self):
        return (self.x-64, self.y-64)

    def current_sprite(self):
        return self.sprite[self.direction][self.frame]

    def get_rect(self, direction):
        if direction == "r":
            pass



class Enemy:
    def __init__(self, hp, attack):
        self.hp = hp
        self.attack = attack

    def update():
        pass
        
    
class Game:
    def __init__(self):
        self.screen = display.set_mode((1280,1024))
        self.world = Map("testmap1")
        self.player = Player((64, 64), "d")

        self.run(60)

        self.enemies = []

    def run(self, framecap, debug=0):
        segoeui = font.SysFont("Arial", 48)
        running = True
        
        self.fps_clock = time.Clock()
        self.frametracker1 = 0

        while running:
            for ev in event.get():
                if ev.type == QUIT:
                    running = False

            self.screen.fill((0, 0, 0))

            self.player_update()


            self.screen.blit(self.world.image, (0, 0), area=(self.world.camera.x * 1280, self.world.camera.y * 1024, 1280, 1024))
            
            self.screen.blit(self.player.current_sprite(), self.player.location())
            
            self.frametracker1 += 1

            if self.fps_clock.get_time() > 0:
                self.screen.blit(segoeui.render(str(1000//self.fps_clock.get_time()),
                    True, (255, 255, 255)), (0, 0))

            self.fps_clock.tick(framecap)
            display.flip()

        quit()
        sys.exit()


    def screenslide(self, direction):
        speed = 16
        if direction == "r":
            for step in range(self.world.camera.x * 1280, (self.world.camera.x+1) * 1280, speed):
                self.player.x -= 15
                self.screenslide2(step)

        elif direction == "l":
            for step in range((self.world.camera.x-1) * 1280, self.world.camera.x * 1280, speed)[::-1]:
                self.player.x += 15
                self.screenslide2(step)

        elif direction == "d":
            for step in range(self.world.camera.y * 1024, (self.world.camera.y+1) * 1024, speed):
                self.player.y -= 15
                self.screenslide2(step)

        elif direction == "u":
            for step in range((self.world.camera.y-1) * 1024, self.world.camera.y * 1024, speed)[::-1]:
                self.player.y += 15
                self.screenslide2(step)
                

    def screenslide2(self, step):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.world.image, (0, 0), area=(self.world.camera.x * 1280, step, 1280, 1024))
        self.screen.blit(self.player.current_sprite(), self.player.location())
        display.flip()

    def player_update(self):
        k = key.get_pressed()
        if k[K_RIGHT]:
            self.player.frame = self.frametracker1 % 20 // 10

            self.player.direction = "r"
            if not self.world.collide((self.player.x+64, self.player.y+16)) and not self.world.collide((self.player.x+64, self.player.y+48)):
                self.player.x += self.player.speed

            if self.player.x > 1216 and self.world.camera.x < 7:
                self.screenslide("r")
                self.world.camera.x += 1

        elif k[K_LEFT]:
            self.player.frame = self.frametracker1 % 20 // 10

            self.player.direction = "l"
            if not self.world.collide((self.player.x+16, self.player.y+16)) and not self.world.collide((self.player.x, self.player.y+48)):
                self.player.x -= self.player.speed

            if self.player.x < 0 and self.world.camera.x > 0:
                self.screenslide("l")
                self.world.camera.x -= 1

        if k[K_DOWN]:
            self.player.frame = self.frametracker1 % 40 // 20

            self.player.direction = "d"
            if not self.world.collide((self.player.x+16, self.player.y+64)) and not self.world.collide((self.player.x+48, self.player.y+64)):
                self.player.y += self.player.speed

            if self.player.y > 960 and self.world.camera.y < 7:
                self.screenslide("d")
                self.world.camera.y += 1

        elif k[K_UP]:
            self.player.frame = self.frametracker1 % 20 // 10

            self.player.direction = "u"
            if not self.world.collide((self.player.x+16, self.player.y)) and not self.world.collide((self.player.x+48, self.player.y)):
                self.player.y -= self.player.speed

            if self.player.y < 0 and self.world.camera.y > 0:
                self.screenslide("u")
                self.world.camera.y -= 1
                


        if k[K_x]:
            if self.player.state != "sword":
                self.frame = 0
                self.player.state = "sword"
            else:
                self.frame += 1

        else:
            if self.player.state == "sword" and self.frame > 30:
                self.frame = 0
                self.player.state = "spin"
            self.player.state = "move"



def main():
    Game()

if __name__ == '__main__':
    main()
