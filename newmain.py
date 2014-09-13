from pygame import *
init()

import sys
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "1,1"

import cProfile

import numpy as np
from random import choice, randrange as rr
from math import *

frametracker1 = 0

def scale4x(image_name):
    """Scales a 48x48 sprite to 192x192"""
    return transform.scale(image.load(image_name), (192, 192))


def spritesheet(base, frames):
    """Returns a tuple of images of length frames from the given base name"""
    return tuple(map(lambda x: scale4x(base + str(x) + ".png"), range(frames)))


def invert(dir):
    """Returns the opposite direction"""
    return {
        "r": "l",
        "l": "r",
        "d": "u",
        "u": "d"
    }.get(dir)


def pixel_invert(surf):
    """Inverts the RGB channels of a surface"""
    surf = surf.copy()
    pixels = surfarray.pixels2d(surf)
    pixels ^= 2 ** 24 - 1
    del pixels
    return surf


class Camera:

    """Tracks the current map view"""

    def __init__(self, image):
        self.x, self.y = 0, 0
        self.max_x = image.get_width() // 1280 + 1
        self.max_y = image.get_height() // 1024 + 1


class Map:

    """Stores map, collision, entities"""

    def __init__(self, name):
        map_name = name

        self.image = image.load("map/%s.png" % map_name).convert()

        self.camera = Camera(self.image)

        # Gets binary tile data from a text file, and assigns it to a 4D Numpy
        # array (grid of screens of grids)
        raw_collision = [list(map(int, list(line)))
                         for line in open("map/" + str(map_name) + ".txt", "r").read().strip().split()]
        self.collision = np.array([[raw_collision[x * 16:x * 16 + 16][y * 20:y * 20 + 20]
                                    for y in range(self.camera.max_x)] for x in range(self.camera.max_y)])  # magic do not touch

        self.enemies = {}
        self.enemies[(0, 0)] = [Enemy("blade", 1000), Enemy("octorok", 3), Enemy("moblin", 5), Enemy("keese", 2), Enemy("eye", 1)]
        self.enemies[(0, 1)] = []

        self.items = {}
        self.items[(0, 0)] = [Item("heart")]
        self.items[(0, 1)] = [Item("heart")]

    def collide(self, location):
        """Checks collision at a given tile"""
        x, y = location
        try:
            return self.collision[int(self.camera.y)][int(self.camera.x)][int(y // 64)][int(x // 64)] == 1
        except IndexError:
            return False
        except TypeError:
            return False


class Sprite:

    """Basic location and collision for 16*16 sprites.
    Sprites are upscaled to 64*64, then padded and centered in a 3*3 grid.
    _________
    |__|__|__|
    |__|{}|__|  {} = sprite
    |__|__|__|  Each box is 64px

    """

    def get_rect(self, direction=None):
        """Returns the hitbox of the sprite.
        If a direction is supplied, a rect of that side is given
        """
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
        """The location to blit the sprite, adjusted for centering"""
        return (self.x - 64, self.y - 64)

    def location(self):
        """Top left corner of the center"""
        return (self.x + 64, self.y + 64)

    def is_immune(self):
        """Returns if the sprite has been hit recently"""
        # Global variable needs to be used because default parameters
        # pass by value, not by name 
        global frametracker1
        return not frametracker1 - 30 > self.immune

    def move(self, direction, amount, world):
        """Collision-savvy movement.  Also returns if the move succeeded."""
        if direction == "r":
            if (not world.collide((self.x + 48 + amount, self.y + 16))
                and not world.collide((self.x + 48 + amount, self.y + 48))
                    and self.x < 1216 - amount):
                self.x += amount
                return True

        elif direction == "l":
            if (not world.collide((self.x + 16 - amount, self.y + 16))
                and not world.collide((self.x + 16 - amount, self.y + 48))
                    and self.x > amount):
                self.x -= amount
                return True

        elif direction == "d":
            if (not world.collide((self.x + 16, self.y + 48 + amount))
                and not world.collide((self.x + 48, self.y + 48 + amount))
                    and self.y < 960 - amount):
                self.y += amount
                return True

        elif direction == "u":
            if (not world.collide((self.x + 16, self.y + 16 - amount))
                and not world.collide((self.x + 48, self.y + 16 - amount))
                    and self.y > amount):
                self.y -= amount
                return True

        return False

    def noclip_move(self, direction, amount):
        if direction == "r":
            self.x += amount
        elif direction == "l":
            self.x -= amount
        elif direction == "d":
            self.y += amount
        elif direction == "u":
            self.y -= amount

    def is_valid(self, world):
        """Returns if the sprite is colliding"""
        return not (world.collide((self.x + 16, self.y + 16))
                    or world.collide((self.x + 48, self.y + 16))
                    or world.collide((self.x + 16, self.y + 48))
                    or world.collide((self.x + 48, self.y + 48)))


class Player(Sprite):

    def __init__(self, location, direction):
        self.x, self.y = location
        self.direction = direction
        self.state = "move"

        self.speed = 4

        self.sprite = {}
        for x in ("rldu"):
            self.sprite[x] = spritesheet("player/" + x, 2)
            self.sprite["sword" + x] = spritesheet("player/sword" + x, 4)
        self.sprite["spin"] = spritesheet("player/spin", 8)

        self.frame = 0
        self.spriteframe = 0

        self.hp = 10
        self.max_hp = 10

        self.immune = -60

    def current_sprite(self):
        if self.state == "move":
            if self.is_immune():
                return pixel_invert(self.sprite[self.direction][self.spriteframe])
            return self.sprite[self.direction][self.spriteframe]

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
            return self.sprite["spin"][self.frame // 3]

    def sword(self):
        if self.state == "sword":
            return {
                "r": Rect(self.x + 64, self.y + 32, 64, 32),
                "l": Rect(self.x - 64, self.y + 32, 64, 32),
                "d": Rect(self.x + 32, self.y + 64, 32, 64),
                "u": Rect(self.x, self.y - 64, 32, 64)
            }[self.direction]

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
            ][self.frame // 3]

        else:
            return Rect(-1, -1, 0, 0)

    def move(self, direction, amount, world):
        if direction == "r":
            if (not world.collide((self.x + 48 + amount, self.y + 16))
                    and not world.collide((self.x + 48 + amount, self.y + 48))):
                self.x += amount
                return True

        elif direction == "l":
            if (not world.collide((self.x + 16 - amount, self.y + 16))
                    and not world.collide((self.x + 16 - amount, self.y + 48))):
                self.x -= amount
                return True

        elif direction == "d":
            if (not world.collide((self.x + 16, self.y + 48 + amount))
                    and not world.collide((self.x + 48, self.y + 48 + amount))):
                self.y += amount
                return True

        elif direction == "u":
            if (not world.collide((self.x + 16, self.y + 16 - amount))
                    and not world.collide((self.x + 48, self.y + 16 - amount))):
                self.y -= amount
                return True

        return False


class Enemy(Sprite):

    def __init__(self, name, hp, location=None, direction=None):
        self.hp, self.max_hp = hp, hp
        self.name = name
        self.state = "move"
        self.speed = 2

        self.sprite = {}
        if self.name in ["octorok", "moblin"]:
            for x in "rldu":
                self.sprite[x] = spritesheet("enemy/" + name + x, 2)

        elif self.name == "keese":
            self.sprite = spritesheet("enemy/" + name, 2)

        elif self.name in ("eye", "blade"):
            self.sprite = spritesheet("enemy/" + name, 1)
            self.xdir = choice("rl")
            self.ydir = choice("du")

        self.dying = spritesheet("entity/dying", 2)

        if location is None:
            self.randomize()
        else:
            self.x, self.y = location

        if direction is None:
            self.direction = choice("rldu")
        else:
            self.direction = direction

        self.alt_direction = "r"
        self.immune = -100

        self.spriteframe = 0
        self.frame = 0

    def current_sprite(self):
        if self.state == "dying":
            return self.dying[self.spriteframe % 8 // 4]

        elif self.name == "octorok" or self.name == "moblin":
            if self.is_immune():
                return pixel_invert(self.sprite[self.direction][self.spriteframe])
            return self.sprite[self.direction][self.spriteframe]

        elif self.name in ("keese", "eye"):
            if self.is_immune():
                return pixel_invert(self.sprite[self.spriteframe])
            return self.sprite[self.spriteframe]

        elif self.name in ("blade"):
            return self.sprite[self.spriteframe]

    def randomize(self):
        self.x, self.y = rr(0, 1232, 64), rr(0, 976, 64)

    def copy(self):
        hp, max_hp = self.max_hp, self.max_hp
        name = self.name
        location = None
        direction = None
        return Enemy(name, hp, location, direction)

    def is_immune(self):
        """Returns if the enemy has been hit recently, or is invulnerable"""
        if self.name in ("blade"):
            return True
        else:
            global frametracker1
            return not frametracker1 - 30 > self.immune


class Item:

    def __init__(self, name, location=None):
        self.name = name
        if location is None:
            self.randomize()
        else:
            self.x, self.y = location
        self.sprite = transform.scale(
            image.load("item/%s.png" % name), (64, 64))

    def randomize(self):
        self.x, self.y = rr(0, 1232, 64), rr(0, 976, 64)

    def current_sprite(self):
        return self.sprite

    def get_rect(self):
        return Rect(self.x, self.y, 64, 64)

    def blit_location(self):
        return (self.x, self.y)


class Entity:

    def __init__(self, name, location, direction, speed, damage):
        self.name = name
        self.sprite = image.load("entities/%s.png" % name)
        self.location = location
        self.direction = direction
        self.speed = speed
        self.damage = damage


class Game:

    def __init__(self):
        self.screen = display.set_mode((1280, 1024))
        self.world = Map("testmap1")
        self.player = Player((64, 64), "d")

        self.enemies = []
        self.enemies2 = [enemy.copy() for enemy in
                         self.world.enemies[(self.world.camera.x, self.world.camera.y)]]
        for enemy in self.enemies2:
            while not enemy.is_valid(self.world):
                enemy.randomize()

        self.items = []
        self.items2 = self.world.items[
            (self.world.camera.x, self.world.camera.y)]

        self.entities, self.entities2 = [], []

        self.run(60, debug=1)

    def run(self, framecap, debug=0):
        self.framecap = framecap
        self.segoeui = font.SysFont("Arial", 48)
        running = True
        self.debug = debug

        self.fps_clock = time.Clock()
        global frametracker1
        frametracker1 = 0

        while running:
            for ev in event.get():
                if ev.type == QUIT:
                    running = False


            self.player_update()
            self.enemy_update()
            self.item_update()
            self.entity_update()

            self.map_blit()
            self.player_blit()
            self.enemy_blit()
            self.item_blit()
            self.entity_blit()
            self.menu_blit()
            self.fps_blit()

            
            frametracker1 += 1
            self.fps_clock.tick(framecap)
            display.flip()

    def screenslide(self, direction):
        speed = 16
        x = self.world.camera.x
        y = self.world.camera.y

        self.world.items[(x, y)] = self.items

        if direction == "r":
            for step in range(x * 1280, (x + 1) * 1280, speed):
                self.player.x -= 15
                self.screenslide2(step)
            self.world.camera.x += 1

        elif direction == "l":
            for step in range((x - 1) * 1280, x * 1280, speed)[::-1]:
                self.player.x += 15
                self.screenslide2(step)
            self.world.camera.x -= 1

        elif direction == "d":
            for step in range(y * 1024, (y + 1) * 1024, speed):
                self.player.y -= 15
                self.screenslide2(step)
            self.world.camera.y += 1

        elif direction == "u":
            for step in range((y - 1) * 1024, y * 1024, speed)[::-1]:
                self.player.y += 15
                self.screenslide2(step)
            self.world.camera.y -= 1

        self.enemies = [enemy.copy() for enemy in
                        self.world.enemies[(self.world.camera.x, self.world.camera.y)]]

        for enemy in self.enemies:
            while not enemy.is_valid(self.world):
                enemy.randomize()

        self.items = self.world.items[
            (self.world.camera.x, self.world.camera.y)]

        self.entities, self.entities2 = [], []

    def screenslide2(self, step):
        self.screen.blit(self.world.image, (0, 0),
                         area=(self.world.camera.x * 1280, step, 1280, 1024))
        self.screen.blit(self.player.current_sprite(),
                         self.player.blit_location())
        self.fps_clock.tick(self.framecap)
        display.flip()

    def enemy_rects(self):
        return list(map(lambda x: x.get_rect(), self.enemies))

    def player_update(self):
        k = key.get_pressed()

        for i in range(len(self.items)):
            if self.player.get_rect().colliderect(self.items[i].get_rect()):
                if self.items[i].name == "heart":
                    self.player.hp += 2
                    self.items[i].name = ""

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
              and not self.player.is_immune()):
            self.player.hp -= 1
            self.player.immune = frametracker1

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
                    self.player.spriteframe = 0
                    self.player.frame = 0

            else:
                if k[K_RIGHT]:
                    self.player.spriteframe = frametracker1 % 20 // 10

                    self.player.direction = "r"

                    self.player.move("r", self.player.speed, self.world)

                    if self.player.x > 1216 and self.world.camera.x < 7:
                        self.screenslide("r")

                elif k[K_LEFT]:
                    self.player.spriteframe = frametracker1 % 20 // 10

                    self.player.direction = "l"

                    self.player.move("l", self.player.speed, self.world)

                    if self.player.x < 0 and self.world.camera.x > 0:
                        self.screenslide("l")

                if k[K_DOWN]:
                    self.player.spriteframe = frametracker1 % 20 // 10

                    self.player.direction = "d"

                    self.player.move("d", self.player.speed, self.world)

                    if self.player.y > 960 and self.world.camera.y < 7:
                        self.screenslide("d")

                elif k[K_UP]:
                    self.player.spriteframe = frametracker1 % 20 // 10

                    self.player.direction = "u"

                    self.player.move("u", self.player.speed, self.world)

                    if self.player.y < 0 and self.world.camera.y > 0:
                        self.screenslide("u")

    def enemy_update(self):
        self.enemies, self.enemies2 = self.enemies2, []

        while len(self.enemies) > 0:
            enemy = self.enemies.pop()

            if enemy.state == "dead":
                if rr(3):
                    self.items.append(
                        Item("heart", location=(enemy.x - 32, enemy.y - 32)))
                continue

            elif enemy.state == "dying":
                if frametracker1 - enemy.frame > 8:
                    enemy.state = "dead"
                enemy.spriteframe += 1
                enemy.spriteframe %= 2

            elif enemy.hp <= 0:
                enemy.state = "dying"
                enemy.frame = frametracker1
                enemy.alt_direction = self.player.direction
                enemy.spriteframe = 0

            elif enemy.get_rect().colliderect(self.player.sword()) and not enemy.is_immune():
                enemy.hp -= 1
                enemy.immune = frametracker1
                enemy.alt_direction = self.player.direction
                enemy.move(self.player.direction, 24, self.world)
                enemy.state = choice("rldu")
                if enemy.name == "moblin":
                    enemy.speed += 0.5

            # Enemy-specific AI
            if enemy.name == "octorok" and enemy.hp > 0:
                if frametracker1 % 30 == 0:
                    enemy.state = choice("rldussss")
                    if enemy.state != "s":
                        enemy.direction = enemy.state
                if enemy.state != "s" and enemy.move(enemy.direction, 4, self.world):
                    enemy.spriteframe = frametracker1 % 20 // 10

            elif enemy.name == "moblin":
                px = self.player.x
                py = self.player.y
                angle = atan2(py - enemy.y, px - enemy.x)
                dirx = (enemy.speed * cos(angle))
                diry = (enemy.speed * sin(angle))
                if dirx > 0:
                    enemy.move("r", abs(dirx), self.world)
                elif dirx < 0:
                    enemy.move("l", abs(dirx), self.world)
                if diry > 0:
                    enemy.move("d", abs(diry), self.world)
                elif diry < 0:
                    enemy.move("u", abs(diry), self.world)
                enemy.spriteframe = frametracker1 % 20 // 10

            elif enemy.name == "keese":
                if frametracker1 % 60 == 0:
                    enemy.state = choice("mmms")
                if frametracker1 % 15 == 0:
                    enemy.direction = choice("lr")
                if enemy.state == "m":
                    enemy.move(choice("ud"), 2, self.world)
                    enemy.move(enemy.direction, 4, self.world)
                    enemy.spriteframe = frametracker1 % 10 // 5

            elif enemy.name == "eye":
                if not enemy.move(enemy.xdir, 4, self.world):
                    enemy.xdir = invert(enemy.xdir)
                if not enemy.move(enemy.ydir, 4, self.world):
                    enemy.ydir = invert(enemy.ydir)

            elif enemy.name == "blade":
                if not enemy.move(enemy.direction, 8, self.world):
                    enemy.direction = invert(enemy.direction)

            self.enemies2.append(enemy)

        self.enemies = self.enemies2

    def item_update(self):
        self.items, self.items2 = self.items2, []

        while len(self.items) > 0:
            item = self.items.pop()
            if item.name == "":
                continue

            self.items2.append(item)

        self.items = self.items2

    def entity_update(self):
        while len(self.entities) > 0:
            entity = self.entities.pop()
            entity.move(entity.direction, entity.speed, self.world)

            self.entities2.append(entity)

        self.entities = self.entities2

    def map_blit(self):
        self.screen.blit(self.world.image, (0, 0),
        area=(self.world.camera.x * 1280, self.world.camera.y * 1024, 1280, 1024))

    def player_blit(self):
        self.screen.blit(self.player.current_sprite(),
                        self.player.blit_location())

    def enemy_blit(self):
        for enemy in self.enemies2:
            if enemy.state != "dead":
                self.screen.blit(enemy.current_sprite(),
                                 enemy.blit_location())

    def item_blit(self):
        for item in self.items2:
                self.screen.blit(item.current_sprite(), item.blit_location())

    def entity_blit(self):
        for entity in self.entities2:
            self.screen.blit()

    def menu_blit(self):
        hp = str(self.player.hp)
        self.screen.blit(self.segoeui.render(hp, True, (255, 255, 255)), (500, 0))

    def fps_blit(self):
        if self.fps_clock.get_time() > 0 and self.debug:
            fps = str(1000 // self.fps_clock.get_time())
            self.screen.blit(self.segoeui.render(fps, True, (255, 255, 255)), (0, 0))



def main():
    cProfile.run("Game()")

if __name__ == '__main__':
    main()
