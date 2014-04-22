from pygame import *
init()

import sys
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1,1"

import numpy as np
from random import randrange as rr, choice

def scale4x(image_name):
    """Scales a 48x48 sprite to 192x192"""
    return transform.scale(image.load(image_name), (192, 192))

def spritesheet(base, frames):
    """Returns a tuple of images of length frames from the given base name"""
    return tuple(map(lambda x: scale4x(base+str(x)+".png"), range(frames)))

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
        self.collision = np.array([[raw_collision[x*16:x*16+16][y*20:y*20+20]
        for y in range(self.camera.max_x)] for x in range(self.camera.max_y)])

        self.enemies = [Enemy(3, 1, "random") for i in range(5)]

        # Sets enemy location
        for i in range(len(self.enemies)):
            self.enemies[i].x, self.enemies[i].y = rr(1280), rr(1024)
            while not self.enemies[i].is_valid(self):
                self.enemies[i].x, self.enemies[i].y = rr(1280), rr(1024)


    def collide(self, location):
        x, y = location
        try:
            return self.collision[int(self.camera.y)][int(self.camera.x)][int(y//64)][int(x//64)] == 1
        except IndexError:
            return False
        except TypeError:
            return False

class Sprite:
    def get_rect(self, direction=None):
        if direction == "r":
            return Rect(self.x + 64, self.y, 4, 64)
        elif direction == "l":
            return Rect(self.x, self.y, 4, 64)
        elif direction == "d":
            return Rect(self.x, self.y + 64, 64, 4)
        elif direction == "u":
            return Rect(self.x, self.y, 64, 4)
        else:
            return Rect(self.x, self.y, 64, 64)

    def blit_location(self):
        return (self.x-64, self.y-64)

    def location(self):
        return (self.x+64, self.y+64)

    def is_immune(self, frametracker1):
        return not frametracker1 - 60 > self.immune

    def move(self, direction, world, amount):
        if direction == "r":
            if (not world.collide((self.x+48+amount, self.y+16))
            and not world.collide((self.x+48+amount, self.y+48))):
                self.x += amount
                return True

        elif direction == "l":
            if (not world.collide((self.x+16-amount, self.y+16))
            and not world.collide((self.x+16-amount, self.y+48))):
                self.x -= amount
                return True

        elif direction == "d":
            if (not world.collide((self.x+16, self.y+48+amount))
            and not world.collide((self.x+48, self.y+48+amount))):
                self.y += amount
                return True

        elif direction == "u":
            if (not world.collide((self.x+16, self.y+16-amount))
            and not world.collide((self.x+48, self.y+16-amount))):
                self.y -= amount
                return True
        
        return False

    def is_valid(self, world):
        return not (world.collide((self.x+16, self.y+16))
        or world.collide((self.x+48, self.y+16))
        or world.collide((self.x+16, self.y+48))
        or world.collide((self.x+48, self.y+48)))




class Player(Sprite):
    def __init__(self, location, direction):
        self.x, self.y = location
        self.direction = direction
        self.state = "move"

        self.speed = 4


        self.sprite = {}
        for x in ("rldu"):
            self.sprite[x] = spritesheet(x, 2)
            self.sprite["sword"+x] = spritesheet("sword"+x, 4)
        self.sprite["spin"] = spritesheet("spin", 8)


        self.frame = 0
        self.walkframe = 0

        self.hp = 10
        self.max_hp = 10

        self.immune = -60


    def current_sprite(self):
        if self.state == "move":
            return self.sprite[self.direction][self.walkframe]
        elif self.state == "sword":
            if self.frame < 5:
                return self.sprite["sword" + self.direction][0]
            elif self.frame < 10:
                return self.sprite["sword" + self.direction][1]
            elif self.frame < 60:
                return self.sprite["sword" + self.direction][2]
            else:
                return self.sprite["sword" + self.direction][2 + self.frame % 6 // 3]

        elif self.state == "spin":
            return self.sprite["spin"][self.frame//3]

    def sword(self):
        if self.state == "sword":
            return {
            "r": (Rect(self.x + 64, self.y - 64, 64, 64),
            Rect(self.x + 64, self.y + 32, 64, 32)),
            "l": (Rect(self.x - 64, self.y - 64, 64, 64),
            Rect(self.x-64, self.y + 32, 64, 32)),
            "d": (Rect(self.x, self.y + 64, 64, 64),
            Rect(self.x + 32, self.y + 64, 32, 64)),
            "u": (Rect(self.x + 64, self.y - 64, 64, 64),
            Rect(self.x, self.y-64, 32, 64))
            }[self.direction][self.frame > 4]

        elif self.state == "spin":
            return [
            Rect(self.x + 64, self.y, 64, 64),
            Rect(self.x + 64, self.y + 64, 64, 64),
            Rect(self.x, self.y + 64, 64, 64),
            Rect(self.x - 64, self.y + 64, 64, 64),
            Rect(self.x - 64, self.y, 64, 64),
            Rect(self.x - 64, self.y - 64, 64, 64),
            Rect(self.x, self.y - 64, 64, 64),
            Rect(self.x + 64, self.y - 64, 64, 64)
            ][self.frame//3]

        else:
            return Rect(-1, -1, 0, 0)



class Enemy(Sprite):
    def __init__(self, hp, attack, ai):
        self.hp, self.maxhp = hp, hp
        self.attack = attack
        self.ai = ai
        self.x, self.y = 0, 0
        self.direction = choice("rldus")
        self.immune = -60

    def reset(self):
        self.hp = hp
        self.x, self.y = rr(1280), rr(1024)


    
class Game:
    def __init__(self):
        self.screen = display.set_mode((1280,1024))
        self.world = Map("testmap1")
        self.player = Player((64, 64), "d")
        

        self.run(60, debug=1)


    def run(self, framecap, debug=0):
        self.framecap = framecap
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
            self.enemy_update()

            self.screen.blit(self.world.image, (0, 0),
            area=(self.world.camera.x * 1280, self.world.camera.y * 1024, 1280, 1024))

            for i in self.world.enemies:
                if i.hp > 0:
                    if i.is_immune(self.frametracker1):
                        colour = ((255, 0, 0), (0, 0, 255))[self.frametracker1 % 8 // 4]
                    else:
                        colour = (255, 0, 0)
                    self.screen.fill(colour, (i.x, i.y, 64, 64))

            self.screen.blit(self.player.current_sprite(), self.player.blit_location())
            
            self.frametracker1 += 1

            if self.fps_clock.get_time() > 0 and debug:
                self.screen.blit(segoeui.render(str(1000//self.fps_clock.get_time()),
                    True, (255, 255, 255)), (0, 0))

            self.screen.blit(segoeui.render(str(self.player.hp), True, (255, 255, 255)), (500, 0))


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
        self.screen.blit(self.player.current_sprite(), self.player.blit_location())
        self.fps_clock.tick(self.framecap)
        display.flip()

    def player_update(self):
        k = key.get_pressed()

        if k[K_x] and self.player.state != "spin":
            if self.player.state == "sword":
                self.player.frame += 1
                if k[K_RIGHT]:
                    self.player.direction = "r"
                if k[K_LEFT]:
                    self.player.direction = "l"
                if k[K_DOWN]:
                    self.player.direction = "d"
                if k[K_UP]:
                    self.player.direction = "u"
            else:
                self.player.frame = 0
                self.player.state = "sword"

        elif (self.player.get_rect().collidelist(self.enemy_rects()) > -1
            and not self.player.is_immune(self.frametracker1)):
            self.player.hp -= 1
            self.player.immune = self.frametracker1      

        else:
            if self.player.state == "sword":
                if self.player.frame > 60:
                    self.player.state = "spin"
                    self.player.frame = 0
                else:
                    self.player.state = "move"
            elif self.player.state == "spin":
                if self.player.frame < 21:
                    self.player.frame += 1
                else:
                    self.player.state = "move"
                    self.player.walkframe = 0
                    self.player.frame = 0

            else:
                if k[K_RIGHT]:
                    self.player.walkframe = self.frametracker1 % 20 // 10

                    self.player.direction = "r"

                    if (not self.world.collide((self.player.x+52, self.player.y+16))
                    and not self.world.collide((self.player.x+52, self.player.y+48))):
                        self.player.x += self.player.speed

                    if self.player.x > 1216 and self.world.camera.x < 7:
                        self.screenslide("r")
                        self.world.camera.x += 1

                elif k[K_LEFT]:
                    self.player.walkframe = self.frametracker1 % 20 // 10

                    self.player.direction = "l"

                    if (not self.world.collide((self.player.x+12, self.player.y+16))
                    and not self.world.collide((self.player.x+12, self.player.y+48))):
                        self.player.x -= self.player.speed

                    if self.player.x < 0 and self.world.camera.x > 0:
                        self.screenslide("l")
                        self.world.camera.x -= 1

                if k[K_DOWN]:
                    self.player.walkframe = self.frametracker1 % 20 // 10

                    self.player.direction = "d"

                    if (not self.world.collide((self.player.x+16, self.player.y+52))
                    and not self.world.collide((self.player.x+48, self.player.y+52))):
                        self.player.y += self.player.speed

                    if self.player.y > 960 and self.world.camera.y < 7:
                        self.screenslide("d")
                        self.world.camera.y += 1

                elif k[K_UP]:
                    self.player.walkframe = self.frametracker1 % 20 // 10

                    self.player.direction = "u"

                    if (not self.world.collide((self.player.x+16, self.player.y+12))
                        and not self.world.collide((self.player.x+48, self.player.y+12))):
                        self.player.y -= self.player.speed

                    if self.player.y < 0 and self.world.camera.y > 0:
                        self.screenslide("u")
                        self.world.camera.y -= 1

    def enemy_update(self):
        for i in range(len(self.world.enemies)):
            if self.world.enemies[i].hp <= 0:
                continue

            if self.world.enemies[i].get_rect().colliderect(self.player.sword()) and \
            not self.world.enemies[i].is_immune(self.frametracker1):
                self.world.enemies[i].hp -= 2 if self.player.state == "spin" else 1
                self.world.enemies[i].immune = self.frametracker1

            else:
                if self.world.enemies[i].ai == "random":
                    if self.frametracker1 % 60 == 0:
                        self.world.enemies[i].direction = choice("rldussss")

                    if (self.world.enemies[i].direction == "r" and self.world.enemies[i].x < 1214
                    and not self.world.collide((self.world.enemies[i].x+64, self.world.enemies[i].y+16))
                    and not self.world.collide((self.world.enemies[i].x+64, self.world.enemies[i].y+48))):
                        self.world.enemies[i].x += 2

                    elif (self.world.enemies[i].direction == "l" and self.world.enemies[i].x > 2
                    and not self.world.collide((self.world.enemies[i].x+16, self.world.enemies[i].y+16))
                    and not self.world.collide((self.world.enemies[i].x, self.world.enemies[i].y+48))):
                        self.world.enemies[i].x -= 2

                    elif (self.world.enemies[i].direction == "d" and self.world.enemies[i].y < 958
                    and not self.world.collide((self.world.enemies[i].x+16, self.world.enemies[i].y+64))
                    and not self.world.collide((self.world.enemies[i].x+48, self.world.enemies[i].y+64))):
                        self.world.enemies[i].y += 2

                    elif (self.world.enemies[i].direction == "u" and self.world.enemies[i].y > 2
                    and not self.world.collide((self.world.enemies[i].x+16, self.world.enemies[i].y))
                    and not self.world.collide((self.world.enemies[i].x+48, self.world.enemies[i].y))):
                        self.world.enemies[i].y -= 2


    def enemy_rects(self):
        return list(map(lambda x: x.get_rect(), self.world.enemies))


def main():
    Game()

if __name__ == '__main__':
    main()
