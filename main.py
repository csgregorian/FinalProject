# Author: Christopher Gregorian
# Website: csgregorian.com
# Name: Legend of Zelda: Link to the Present
# Completed: 03:18 AM, June 16th, 2014


# # # Imports # # #
# # Built-Ins # #
import sys
import os
import cProfile  # Debugging and optimizing
from random import choice, randrange as rr
from math import *
from time import sleep

# # External Modules # #
try:
    from pygame import *
    init()
    mixer.init()
except:
    print("Sorry, pygame is not installed.")


# # # Checks # # #
# if sys.version_info[:2] != (3, 2):
#     print("Sorry, you need version 3.2 of Python to run this program.")
#     raise SystemExit


# # # Functions # # #
def scale4x(image_name):
    """Scales an image"""
    surf = image.load(image_name)
    return transform.scale(surf, (surf.get_width()*4, surf.get_height()*4))

# Deprecated, actual sprite sheets have been implemented now
def playersheet(base, frames):
    """Returns a tuple of images of length frames from the given base name"""
    return tuple(scale4x("%s%s.png" % (base, str(x))) for x in range(frames))

def spritesheet(filepath, frames, subsections):
    """Returns a dictionary of sprites with a given number of frames
    Splits vertically by section, horizontally by frame"""
    sprites = scale4x("%s.png" % filepath)
    splitsheet = {}

    for index, section in enumerate(subsections):
        splitsheet[section] = tuple(sprites.subsurface((frame * 64, index * 64, 64, 64)) for frame in range(0,frames))
        
    return splitsheet

def reverse_direction(dir):
    """Returns the opposite direction"""
    return {
        R: L,
        L: R,
        D: U,
        U: D
    }.get(dir)

def invert_pixels(surf):
    """Inverts the RGB channels of a surface
    Use bitwise xor to invert really quickly."""
    surf = surf.copy()
    pixels = surfarray.pixels2d(surf)
    pixels ^= 2 ** 24 - 1
    del pixels
    return surf

# # # Global Variables # # #
current_frame = 0
bigfont = font.SysFont("Courier New", 64)
smallfont = font.SysFont("Courier New", 16)


# # Sounds # #

# A dictionary would have been nice here, but the sounds had too much of a delay.
mixer.music.load("sound/theme_song.wav")
beep = mixer.Sound("sound/beep.wav")
ding = mixer.Sound("sound/item.wav")
start_sound = mixer.Sound("sound/begin.wav")
# Switches between 3 sword sounds
sword_sound = tuple(mixer.Sound("sound/sword%d.wav" % x) for x in range(1,4))
spin_sound = mixer.Sound("sound/spin.wav")
hit_sound = mixer.Sound("sound/hit.wav")
dead_sound = mixer.Sound("sound/dead.wav")
phit_sound = mixer.Sound("sound/phit.wav")
pdead_sound = mixer.Sound("sound/pdead.wav")
shock_sound = mixer.Sound("sound/shock.wav")
tele_sound = mixer.Sound("sound/tele.wav")
shaking_sound = mixer.Sound("sound/shaking.wav")
win_sound = mixer.Sound("sound/win.wav")
gameover_sound = mixer.Sound("sound/gameover.wav")

# # Images # #
sword_sprite = scale4x("item/sword.png")
slingshot_sprite = scale4x("item/slingshot.png")
pegasus_sprite = scale4x("item/pegasus.png")

# Sets screen to the top left
os.environ['SDL_VIDEO_WINDOW_POS'] = "1,1"

# # Constants # #
HEART = "heart"
SEED = "seed"
SHOOT = "shoot"
SWORD = "sword"
SPIN = "spin"
DEAD = "dead"
DYING = "dying"
MOVE = "move"
R, L, D, U = "r", "l", "d", "u"
# I gave up making constants around here
# Magic strings are great



# # # Classes # # #

class Map:
    """Stores map, collision, entities"""

    def __init__(self, name):
        self.map_name = name

        # .convert() is important here, removing a channel kicks up the framerate a ton
        self.image = scale4x("map/%s.png" % self.map_name).convert()

        # Tracks current screen, number of screens
        self.x, self.y = 0, 0
        self.max_x = 4
        self.max_y = 4

        # Gets binary map data
        self.raw_collision = open("map/%s.txt" % (self.map_name), "r").read().strip().split()

        # !!!!!!!!!!!!!!!!!!!
        # This collision system broke on me two days before this thing is due
        # let it be known that it took me 3 hours to fix this
        # Things I have learned:
        # multidimensional lists are literally the worst thing to exist ever
        # numpy sucks majorly
        # it's okay to throw code style out the window sometimes

        # for i in self.raw_collision:
        #     print(i)
        
        # self.collision = np.array([[np.array(self.raw_collision[x * 16:x * 16 + 16][y * 16:y * 16 + 16])
        #                             for y in range(self.max_x)] for x in range(self.max_y)])  # magic do not touch

        # # try:
        # #     print(self.collision[:][1])
        # #     print(self.collision.shape)
        # #     print(self.collision[:].shape)
        # #     print(type(self.collision))
        # #     print(type(self.collision[0]))
        # #     print(type(self.collision[0][0]))
        # #     print(type(self.collision[0][0][0]))
        # #     print(type(self.collision[0][0][0][0]))
        # # except:
        # #     pass

        # self.collision = {}
        # for x in range(self.max_x):
        #     for y in range(self.max_y):
        #         self.collision[(x, y)] = self.raw_collision[y*16:y*16+16][x*16:x*16+16]




        # again, don't need unnecessary multidimensional lists
        # in this case they don't add anything

        # there were some blank enemies here that just acted as invisible traps
        # but they were randomizing their location every time for no reason
        # I just removed them instead
        self.enemies = {
        (0, 0): [],
        (0, 1): [Enemy("octorok_red", 1, (5*64, 7*64)),
                Enemy("octorok_red", 1, (15*64, 9*64))],
        (0, 2): [Enemy("octorok_red", 1),
                Enemy("octorok_red", 1),
                Enemy("octorok_blue", 2)],
        (0, 3): [Enemy("octorok_blue", 2, (2*64, 2*64)),
                Enemy("octorok_red", 1, (15*64, 8*64)),
                Enemy("octorok_blue", 2, (12*64, 11*64))],
        (0, 4): [Enemy("ghost", 3),
                Enemy("ghost", 2),
                Enemy("ghost", 3)],
        (1, 0): [Enemy("keese_black", 2),
                Enemy("keese_black", 2),
                Enemy("keese_black", 2),
                Enemy("blade_yellow", 1, (3*64, 3*64), R),
                Enemy("blade_red", 1, (9*64, 8*64), R),
                Enemy("blade_green", 1, (15*64, 11*64)),
                Enemy("eye", 1)],
        (1, 1): [Enemy("blade_yellow", 1, (17*64, 10*64), R),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1)],
        (1, 2): [Enemy("blade_blue", 1, (17*64, 13*64), R),
                Enemy("blade_green", 1, (7*64, 11*64), R),
                Enemy("blade_blue", 1, (5*64, 9*64), D),
                Enemy("blade_red", 1, (13*64, 8*64), L),
                Enemy("blade_green", 1, (2*64, 1*64), D),
                Enemy("blade_red", 1, (6*64, 3*64), R),
                Enemy("blade_yellow", 1, (10*64, 5*64))],
        (1, 3): [Enemy("keese_black", 1, (4*64, 4*64)),
                Enemy("keese_black", 1, (15*64, 12*64)),
                Enemy("keese_black", 1),
                Enemy("keese_black", 1)],
        (2, 0): [Enemy("moblin_red", 2),
                Enemy("moblin_red", 2)],
        (2, 1): [Enemy("moblin_red", 3),
                Enemy("electro", 1),
                Enemy("electro", 1)],
        (2, 2): [Enemy("skull", 1, (1*64, 1*64)),
                Enemy("skull", 1, (1*64, 14*64)),
                Enemy("skull", 1, (18*64, 1*64)),
                Enemy("skull", 1, (18*64, 14*64))],
        (2, 3): [Enemy("skull", 1, (6*64, 12*64), D),
                Enemy("skull", 1, (9*64, 14*64), U),
                Enemy("skull", 1, (12*64, 14*64), U),
                Enemy("octorok_red", 1)],
        (3, 0): [],
        (3, 1): [],
        (3, 2): [Enemy("moblin_blue", 4, (10*64, 7*64)),
                Enemy("moblin_blue", 2, (9*64, 7*64))],
        (3, 3): [Enemy("octorok_blue", 2),
                Enemy("electro", 2),
                Enemy("eye", 2),
                Enemy("eye", 2)]
        }

        self.items = {
        (0, 0): [Item("heart", (10*64, 8*64))],
        (0, 1): [],
        (0, 2): [],
        (0, 3): [Item("sword", (4*64, 13*64))],
        (0, 4): [Item("container", (2*64, 2*64))],
        (1, 0): [],
        (1, 1): [],
        (1, 2): [Item("heart", (3*64, 9*64)),
                Item("heart", (3*64, 11*64)),
                Item("heart", (8*64, 9*64)),
                Item("heart", (11*64, 9*64)),
                Item("heart", (14*64, 9*64)),
                Item("heart", (11*64, 6*64)),
                Item("heart", (13*64, 6*64)),
                Item("container", (4*64, 4*64)),
                Item("seed", (3*64, 14*64))],
        (1, 3): [],
        (2, 0): [Item("pegasus", (3*64, 1*64))],
        (2, 1): [Item("heart", (1*64, 1*64)),
                Item("heart", (6*64, 9*64))],
        (2, 2): [Item("container", (9*64, 13*64))],
        (2, 3): [Item("slingshot", (4*64, 4*64)),
                Item("seed", (4*64, 13*64))],
        (3, 0): [],
        (3, 1): [],
        (3, 2): [Item("heart", (2*64, 6*64)),
                Item("container", (17*64, 6*64)),
                Item("triforce", (9*64, 4*64)),
                Item("triforce", (10*64, 4*64))],
        (3, 3): [Item("seed", (6*64, 6*64))]
        }

        self.npcs = {
        (0, 0): [NPC((8*64, 12*64),
                    "Caution!",
                    "Monsters ahead!",
                    "It's dangerous to go alone!",
                    "...",
                    "...",
                    "...",
                    "I'm a sign, ...",
                    "I don't have anything for you!")],
        (0, 1): [],
        (0, 2): [],
        (0, 3): [NPC((18*64, 10*64),
                    "Be careful!",
                    "I heard this dungeon is scary!",
                    "Make sure you're prepared!")],
        (0, 4): [NPC((16*64, 5*64),
                    "I left something in my grave.",
                    "If you can find it, it's yours!")],
        (1, 0): [],
        (1, 1): [],
        (1, 2): [NPC((2*64, 13*64),
                    "I found this in my hole.",
                    "You might need it later!")],
        (1, 3): [],
        (2, 0): [NPC((18*64, 5*64),
                    "Those mushrooms are poisonous!",
                    "*dies*")],
        (2, 1): [],
        (2, 2): [NPC((10*64, 13*64),
                    "What happened here?",
                    "It looks like it ...",
                    "used to be a city.",
                    "Hyrule's a mess...",
                    "I hope somebody helps us soon!")],
        (2, 3): [],
        (3, 0): [],
        (3, 1): [],
        (3, 2): [],
        (3, 3): [NPC((7*64, 6*64),
                    "The northern peak is up ahead!",
                    "I sense a great evil...",
                    "Save us, hero!")]
        }

    def collide(self, location):
        """Checks collision at a given tile"""
        x, y = location
        collide = False
        try:
            return self.raw_collision[int(self.y * 16 + (y//64))][int(self.x * 20 + (x//64))] == "1"
        except IndexError as e:
            # random debugging stuff
            print("index")
            print(int(self.y))
            print(int(self.x))
            print(y//64)
            print(x//64)
            print(e)
            return False
        except TypeError as e:
            print("type")
            print (e)
            return False
        except Exception:
            print("")



class Sprite:
    """Basic location and collision for 16x16 sprites upscaled to 64x64."""
    
    @property
    def location(self):
        return (self.x, self.y)

    @property
    def is_immune(self):
        """Returns if the sprite has been has been hit in the past half second"""
        global current_frame
        return not current_frame - 30 > self.immune
    
    def move(self, direction, amount, world):
        """Collision-savvy movement.  Also returns if the move succeeded.
        Also accounts for going off-screen.  Also bashy as anything."""
        if direction == R:
            if (not world.collide((self.x + 48 + amount, self.y + 16))
                and not world.collide((self.x + 48 + amount, self.y + 48))
                    and self.x < 1216 - amount):
                self.x += amount
                return True

        elif direction == L:
            if (not world.collide((self.x + 16 - amount, self.y + 16))
                and not world.collide((self.x + 16 - amount, self.y + 48))
                    and self.x > amount):
                self.x -= amount
                return True

        elif direction == D:
            if (not world.collide((self.x + 16, self.y + 48 + amount))
                and not world.collide((self.x + 48, self.y + 48 + amount))
                    and self.y < 960 - amount):
                self.y += amount
                return True

        elif direction == U:
            if (not world.collide((self.x + 16, self.y + 16 - amount))
                and not world.collide((self.x + 48, self.y + 16 - amount))
                    and self.y > amount):
                self.y -= amount
                return True

        return False

    def noclip_move(self, direction, amount):
        """Alternate move interface, instead of direct variable access"""
        if direction == R:
            self.x += amount
        elif direction == L:
            self.x -= amount
        elif direction == D:
            self.y += amount
        elif direction == U:
            self.y -= amount

    def is_valid(self, world):
        """Returns if the sprite is colliding
        Checks the corners in the center 32x32 area"""
        return not (world.collide((self.x + 16, self.y + 16))
                    or world.collide((self.x + 48, self.y + 16))
                    or world.collide((self.x + 16, self.y + 48))
                    or world.collide((self.x + 48, self.y + 48)))


    def get_rect(self, direction=None):
        """Returns the hitbox of the sprite.
        If a direction is supplied, a rect of that side is given
        """
        return {
            R: Rect(self.x + 60, self.y + 4,   4, 56),
            L: Rect(self.x,      self.y + 4,   4, 56),
            D: Rect(self.x + 4,  self.y + 60, 56, 4),
            U: Rect(self.x + 4,  self.y,      56, 4),
            None: Rect(self.x, self.y, 64, 64)
        }[direction]


class Player(Sprite):
    def __init__(self, location, direction):
        self.x, self.y = location
        self.direction = direction
        self.state = MOVE

        self.speed = 4

        # Creates sprite dict
        self.sprite = {}
        for x in ("rldu"):
            self.sprite[x] = playersheet("player/" + x, 2)
            self.sprite[SWORD + x] = playersheet("player/sword" + x, 4)
        self.sprite[SPIN] = playersheet("player/spin", 8)

        # Tracks time since last state change, sprite change
        self.frame = 0
        self.spriteframe = 0

        # I had to keep increasing this because it was too hard
        # or maybe I'm just bad at my own game
        self.hp = 10
        self.max_hp = 10

        self.immune = -30

        # tracks inventory
        self.has_sword = False
        self.has_slingshot = False
        self.has_pegasus = False
        self.seeds = 5

        # tracks time since last used
        self.pegasus = 0

    @property
    def sword(self):
        """Returns location of sword"""
        if self.state == SWORD:
            return {
                R: Rect(self.x + 64, self.y + 32, 64, 32),
                L: Rect(self.x - 64, self.y + 32, 64, 32),
                D: Rect(self.x + 32, self.y + 64, 32, 64),
                U: Rect(self.x, self.y - 64, 32, 64)
            }[self.direction]

        elif self.state == SPIN:
            size = (64, 64)
            return [
                Rect(self.x + 64, self.y, *size),
                Rect(self.x + 64, self.y + 64, *size),
                Rect(self.x, self.y + 64, *size),
                Rect(self.x - 64, self.y + 64, *size),
                Rect(self.x - 64, self.y, *size),
                Rect(self.x - 64, self.y - 64, *size),
                Rect(self.x, self.y - 64, *size),
                Rect(self.x + 64, self.y - 64, *size)
            ][self.frame // 3]

        else:
            return Rect(-1, -1, 0, 0)

    def move(self, direction, amount, world):
        """Same as the inherited Sprite move, but allows off-screen movement"""
        if direction == R:
            if (not world.collide((self.x + 48 + amount, self.y + 16))
                    and not world.collide((self.x + 48 + amount, self.y + 48))):
                self.x += amount
                return True

        elif direction == L:
            if (not world.collide((self.x + 16 - amount, self.y + 16))
                    and not world.collide((self.x + 16 - amount, self.y + 48))):
                self.x -= amount
                return True

        elif direction == D:
            if (not world.collide((self.x + 16, self.y + 48 + amount))
                    and not world.collide((self.x + 48, self.y + 48 + amount))):
                self.y += amount
                return True

        elif direction == U:
            if (not world.collide((self.x + 16, self.y + 16 - amount))
                    and not world.collide((self.x + 48, self.y + 16 - amount))):
                self.y -= amount
                return True

        return False

    @property
    def current_sprite(self):
        """Returns current frame based on state"""
        if self.state == MOVE:
            if self.is_immune:
                return invert_pixels(self.sprite[self.direction][self.spriteframe])
            return self.sprite[self.direction][self.spriteframe]

        elif self.state == SWORD:
            swordsprite = self.sprite[SWORD + self.direction]
            # Irregular frame timings
            if self.frame < 2:
                return swordsprite[0]
            elif self.frame < 10:
                return swordsprite[1]
            elif self.frame < 30:
                return swordsprite[2]
            else:
                return swordsprite[2 + self.frame % 6 // 3]

        elif self.state == SPIN:
            return self.sprite[SPIN][self.frame // 3]

        else:
            return self.sprite[self.direction][self.spriteframe]

    def hurt(self, damage, direction, world):
        # Shortcut to knockback, immunity, sound, and damage all at once
        if self.is_immune:
            return False
        else:
            self.hp -= 1
            self.move(direction, 24, world)
            self.immune = current_frame
            phit_sound.play()
            return True

    @property
    def blit_location(self):
        """The location to blit the sprite, adjusted for centering"""
        return (self.x - 64, self.y - 64)


class Enemy(Sprite):

    # This is cool, by making these part of the class instead of an instance
    # All of the instances can access this, preventing having to reload every 
    # image on init
    sprite = {}
    for name in ["octorok_red", "octorok_blue", "moblin_red", "moblin_blue"]:
        sprite[name] = spritesheet("enemy/%s" % name, 2, (R, L, D, U))

    for name in ["keese_black", "ghost", "skull"]:
        sprite[name] = spritesheet("enemy/%s" % name, 2, (None,))

    for name in ["eye", "blade_blue", "blade_red", "blade_green", "blade_yellow"]:
        sprite[name] = spritesheet("enemy/%s" % name, 1, (None,))

    for name in ["electro"]:
        sprite[name] = spritesheet("enemy/%s" % name, 3, (None,))

    sprite["blank"] = scale4x("enemy/blank.png")

    sprite[DYING] = spritesheet("entity/dying", 2, (None,)) 


    def __init__(self, name, hp, location=None, direction=None):
        self.hp, self.max_hp = hp, hp
        self.name = name
        self.state = MOVE
        
        # 06-01 Change this
        # 06-16 I'm just going to leave this in case it breaks anything
        self.speed = 2

        # argvalue keeps track of the original passed, to be used for copying
        self.arglocation = location
        if location is None:
            self.randomize()
        else:
            self.x, self.y = location

        self.argdirection = direction
        if direction is None and name != "skull":
            self.direction = choice("rldu")
        else:
            self.direction = direction

        if self.name == "eye":
            self.xdir = choice("rl")
            self.ydir = choice("du")

        self.alt_direction = R
        self.immune = -100

        self.spriteframe = 0
        self.frame = 0

    @property
    def current_sprite(self):
        if self.state == DYING:
            return self.sprite[DYING][None][self.spriteframe % 8 // 4]

        elif self.name in ("octorok_red", "octorok_blue", "moblin_red", "moblin_blue"):
            if self.is_immune:
                return invert_pixels(self.sprite[self.name][self.direction][self.spriteframe])
            return self.sprite[self.name][self.direction][self.spriteframe]

        elif self.name in ("keese_black", "eye", "electro", "ghost"):
            if self.is_immune:
                return invert_pixels(self.sprite[self.name][None][self.spriteframe])
            return self.sprite[self.name][None][self.spriteframe]

        elif self.name in ("blade_blue", "blade_red", "blade_green", "blade_yellow", "skull"):
            return self.sprite[self.name][None][self.spriteframe]

        elif self.name == "blank":
            return self.sprite["blank"]

    def randomize(self):
        # just gives it a location on the map
        self.x, self.y = rr(0, 1232, 64), rr(0, 976, 64)

    def copy(self):
        # deepcopy doesn't work on pygame surfaces, so we use this
        # two weeks later - oh wait I don't have surfaces in the instances anymore
        # oh well
        hp, max_hp = self.max_hp, self.max_hp
        name = self.name
        location = self.arglocation
        direction = self.argdirection
        return Enemy(name, hp, location, direction)

    @property
    def is_immune(self):
        """Returns if the enemy has been hit recently, or is invulnerable"""
        if self.name in ("blade_blue", "blade_green", "blade_red", "blade_yellow",
                        "blank", "skull"):
            return True
        else:
            return not current_frame - 30 > self.immune

    def hurt(self, damage, direction, world):
        if self.is_immune:
            return False
        else:
            self.hp -= 1
            self.move(direction, 24, world)
            return True

class Item:

    def __init__(self, name, location=None):
        self.name = name
        if location is None:
            self.randomize()
        else:
            self.x, self.y = location
        self.sprite = scale4x("item/%s.png" % name)

    def randomize(self):
        self.x, self.y = rr(0, 1232, 64), rr(0, 976, 64)

    @property
    def current_sprite(self):
        return self.sprite

    def get_rect(self):
        return Rect(self.x, self.y, 64, 64)

    @property
    def location(self):
        return (self.x, self.y)


class Entity(Sprite):

    def __init__(self, name, location, direction, speed, damage, bounce=None):
        self.name = name
        self.sprite = scale4x("entity/%s.png" % name)
        self.x, self.y = location
        self.direction = direction
        self.speed = speed
        # If damage > 0, hurts player, otherwise hurts enemies
        self.damage = damage
        self.bounce = bounce

    @property
    def current_sprite(self):
        return self.sprite

class NPC:

    def __init__(self, location, *args):
        self.x, self.y = location
        self.messages = args

    def get_rect(self):
        return Rect(self.x, self.y, 64, 64)


class Game:
    """This is where the magic happens"""
    def __init__(self):
        """Some magic happens here, just to set it up"""
        self.screen = display.set_mode((1280, 1024), DOUBLEBUF | FULLSCREEN | HWSURFACE)
        self.world = Map("finalmap")
        self.player = Player((11*64, 3*64), D)

        self.enemies = []
        self.enemies2 = [enemy.copy() for enemy in
                         self.world.enemies[(self.world.x, self.world.y)]]

        for enemy in self.enemies2:
            while not enemy.is_valid(self.world):
                enemy.randomize()

        self.items = []
        self.items2 = self.world.items[
            (self.world.x, self.world.y)]

        self.entities, self.entities2 = [], []


        self.run(60)

    def run(self, framecap, debug=0):
        """The rest happens here
        Debug just acts as a quick switch between test build and production build"""
        self.framecap = framecap
        running = True
        self.debug = debug

        self.fps_clock = time.Clock()

        global current_frame
        current_frame = 0

        if debug != 1:
            self.message("Welcome to Hyrule, Link! [x]",
                "You are the Hero of Time. [x]",
                "As the Great Deku Tree,   ... [x]",
                "and protector of this forest,   ...",
                "I give you a mission:",
                "You must retrieve the Triforce   ...",
                "to save Hyrule!",
                "View your inventory with Shift",
                "Press X to read signs   ...",
                "and talk to people.",
                "Good luck and have fun!")

        start_sound.play()

        mixer.music.play(loops = -1)


        while running:
            for ev in event.get():
                if ev.type == QUIT:
                    running = False
                elif ev.type == KEYDOWN:
                    if ev.key == K_x:
                        self.npc_update() #Activates message things.

            self.player_update()
            self.enemy_update()
            self.item_update()
            self.entity_update()
            self.check()

            self.map_blit()
            self.player_blit()
            self.enemy_blit()
            self.item_blit()
            self.entity_blit()
            self.menu_blit()
            self.fps_blit()

            # for x in range(20):
            #     for y in range(16):
            #         if self.world.collide((x*64, y*64)):
            #             draw.rect(self.screen, (255, 0, 0), (x*64, y*64, 64, 64))
        
            current_frame += 1
            self.fps_clock.tick(framecap)
            display.flip()

    def screenslide(self, direction):
        """switches between screens"""
        speed = 16
        x = self.world.x
        y = self.world.y

        self.world.items[(x, y)] = self.items

        if direction == R:
            for step in range(x * 1280, (x + 1) * 1280, speed):
                self.player.x -= 15
                self.screenslide2(step, direction)
            self.world.x += 1

        elif direction == L:
            for step in range((x - 1) * 1280, x * 1280, speed)[::-1]:
                self.player.x += 15  
                self.screenslide2(step, direction)
            self.world.x -= 1

        elif direction == D:
            for step in range(y * 1024, (y + 1) * 1024, speed):
                self.player.y -= 15
                self.screenslide2(step, direction)
            self.world.y += 1

        elif direction == U:
            for step in range((y - 1) * 1024, y * 1024, speed)[::-1]:
                self.player.y += 15
                self.screenslide2(step, direction)
            self.world.y -= 1

        # initializes all the appropriate enemy, entity, item etc.
        self.enemies = [enemy.copy() for enemy in
                        self.world.enemies[(self.world.x, self.world.y)]]

        for enemy in self.enemies:
            while not enemy.is_valid(self.world):
                enemy.randomize()

        self.items = self.world.items[
            (self.world.x, self.world.y)]

        self.entities, self.entities2 = [], []

    def screenslide2(self, step, direction):
        """this does the animating part"""
        if direction in (U, D):
            self.screen.blit(self.world.image, (0, 0),
                             area=(self.world.x * 1280, step, 1280, 1024))
        elif direction in (R, L):
            self.screen.blit(self.world.image, (0, 0),
                             area=(step, self.world.y * 1024, 1280, 1024))
        self.screen.blit(self.player.current_sprite,
                         self.player.blit_location)
        self.fps_clock.tick(self.framecap)
        display.flip()

    @property
    def enemy_rects(self):
        return [x.get_rect() for x in self.enemies]

    def player_update(self):
        k = key.get_pressed()
        player = self.player
        items = self.items

        if not player.is_immune:
            for dir in (R, L, D, U):
                if player.get_rect(dir).collidelist(self.enemy_rects) > -1:
                    player.hurt(1, reverse_direction(dir), self.world)

        # state changing 
        # Activates speed boost
        if k[K_a] and player.pegasus == 0 and player.has_pegasus and player.seeds > 0:
            # increases speed
            player.seeds -= 1
            player.pegasus = 300

        # Activates sword
        if k[K_x] and player.state != SPIN and player.has_sword:
            if player.state == SWORD:
                # holds down sword here
                player.frame += 1
                if k[K_RIGHT]:
                    player.direction = R
                if k[K_LEFT]:
                    player.direction = L
                if k[K_DOWN]:
                    player.direction = D
                if k[K_UP]:
                    player.direction = U
            else:
                # slashes sword here
                player.frame = 0
                player.state = SWORD
                choice(sword_sound).play()


        elif k[K_z] and player.state != SHOOT and player.has_slingshot and player.seeds > 0:
            player.state = SHOOT
            self.frame = 0

        else:
            # mostly state handling here
            if player.pegasus > 0:
                player.pegasus -= 1

            if player.state == SHOOT:
                player.frame += 1
                if player.frame == 5:
                    self.entities.append(
                        Entity("seed", player.location, player.direction, 16, -1, bounce=0)
                        )
                    player.seeds -= 1

                if player.frame > 30:
                    player.state = MOVE
                    player.frame = 0

            if player.state == SWORD:
                if player.frame > 30:

                    player.state = SPIN
                    player.frame = 0
                    spin_sound.play()
                else:
                    player.state = MOVE

            elif player.state == SPIN:
                if player.frame < 21:
                    player.frame += 1
                else:
                    player.state = MOVE
                    player.spriteframe = 0
                    player.frame = 0

            else:
                # then movement
                if k[K_RIGHT]:
                    player.spriteframe = current_frame % 20 // 10

                    player.direction = R

                    for i in range((player.pegasus > 0) + 1):
                        player.move(R, player.speed, self.world)

                    if player.x > 1216 and self.world.x < 7:
                        self.screenslide(R)

                elif k[K_LEFT]:
                    player.spriteframe = current_frame % 20 // 10

                    player.direction = L

                    for i in range((player.pegasus > 0) + 1):
                        player.move(L, player.speed, self.world)

                    if player.x < 0 and self.world.x > 0:
                        self.screenslide(L)

                if k[K_DOWN]:
                    player.spriteframe = current_frame % 20 // 10

                    player.direction = D

                    for i in range((player.pegasus > 0) + 1):
                        player.move(D, player.speed, self.world)

                    if player.y > 960 and self.world.y < 7:
                        self.screenslide(D)

                elif k[K_UP]:
                    player.spriteframe = current_frame % 20 // 10

                    player.direction = U

                    for i in range((player.pegasus > 0) + 1):
                        player.move(U, player.speed, self.world)

                    if self.player.y < 0 and self.world.y > 0:
                        self.screenslide(U)


    def enemy_update(self):

        while len(self.enemies) > 0:
            enemy = self.enemies.pop()

            if enemy.state == DEAD:
                # chooses an item to drop
                item = rr(3)
                if item == 0:
                    self.items.append(Item(HEART, location=(enemy.location)))
                elif item == 1:
                    self.items.append(Item(SEED, location=(enemy.location)))

                dead_sound.play()

                continue

            elif enemy.state == DYING:
                if current_frame - enemy.frame > 8:
                    enemy.state = DEAD
                enemy.spriteframe += 1
                enemy.spriteframe %= 2

            elif enemy.hp <= 0:
                enemy.state = DYING
                enemy.frame = current_frame
                enemy.alt_direction = self.player.direction
                enemy.spriteframe = 0

            elif enemy.get_rect().colliderect(self.player.sword) and not enemy.is_immune:
                enemy.hp -= 1
                enemy.immune = current_frame
                enemy.alt_direction = self.player.direction
                enemy.move(self.player.direction, 24, self.world)
                enemy.state = choice("rldu")
                if enemy.name == "moblin_blue":
                    enemy.speed += 0.5
                    hit_sound.play()
                elif enemy.name == "electro":
                    # shocks the player on hit
                    self.player.hp -= 1
                    shock_sound.play()
                else:
                    hit_sound.play()

            # Enemy-specific AI
            if enemy.name in ("octorok_red", "octorok_blue"):
                if current_frame % 30 == 0:
                    enemy.state = choice("rldussss")
                    if enemy.state != "s":
                        enemy.direction = enemy.state
                if enemy.state != "s" and enemy.move(enemy.direction, 4, self.world):
                    enemy.spriteframe = current_frame % 20 // 10
                if rr(60) == rr(60):
                    self.entities2.append(
                    Entity("bullet%s" % enemy.direction, (enemy.location), enemy.direction, 8, 1))

            if enemy.name in ("electro"):
                if current_frame % 30 == 0:
                    enemy.state = choice("rldu")
                    if enemy.state != "s":
                        enemy.direction = enemy.state
                enemy.move(enemy.direction, 4, self.world)
                enemy.spriteframe = current_frame % 30 // 10

            elif enemy.name in ("moblin_red", "moblin_blue"):
                px = self.player.x
                py = self.player.y
                angle = atan2(py - enemy.y, px - enemy.x)
                dirx = (enemy.speed * cos(angle))
                diry = (enemy.speed * sin(angle))
                if dirx > 0:
                    enemy.move(R, abs(dirx), self.world)
                elif dirx < 0:
                    enemy.move(L, abs(dirx), self.world)
                if diry > 0:
                    enemy.move(D, abs(diry), self.world)
                elif diry < 0:
                    enemy.move(U, abs(diry), self.world)
                enemy.spriteframe = current_frame % 20 // 10
                if rr(100) == rr(100):
                    self.entities2.append(
                    Entity("bullet%s" % enemy.direction, (enemy.location), enemy.direction, 8, 1))

            elif enemy.name == "keese_black" or enemy.name == "ghost":
                if current_frame % 60 == 0:
                    enemy.state = choice("mmms")
                if current_frame % 15 == 0:
                    enemy.direction = choice("lr")
                if enemy.state == "m":
                    enemy.move(choice("ud"), 2, self.world)
                    enemy.move(enemy.direction, 4, self.world)
                    enemy.spriteframe = current_frame % 10 // 5

            elif enemy.name == "eye":
                if not enemy.move(enemy.xdir, 4, self.world):
                    enemy.xdir = reverse_direction(enemy.xdir)
                if not enemy.move(enemy.ydir, 4, self.world):
                    enemy.ydir = reverse_direction(enemy.ydir)

            # speed's based on colour
            elif enemy.name == "blade_blue":
                if not enemy.move(enemy.direction, 2, self.world):
                    enemy.direction = reverse_direction(enemy.direction)

            elif enemy.name == "blade_green":
                if not enemy.move(enemy.direction, 4, self.world):
                    enemy.direction = reverse_direction(enemy.direction)

            elif enemy.name == "blade_red":
                if not enemy.move(enemy.direction, 8, self.world):
                    enemy.direction = reverse_direction(enemy.direction)

            elif enemy.name == "blade_yellow":
                if not enemy.move(enemy.direction, 16, self.world):
                    enemy.direction = reverse_direction(enemy.direction)

            elif enemy.name == "skull":
                if current_frame % 60 == 0:
                    if enemy.direction is not None:
                        self.entities.append(
                        Entity("note", (enemy.location), enemy.direction, 8, 1))
                    else:
                        for direction in (R, L, D, U):
                            self.entities.append(
                            Entity("note", (enemy.location), direction, 8, 1))
                enemy.spriteframe = current_frame % 20 // 10


            # if it gets this far, it's alive
            self.enemies2.append(enemy)

        self.enemies, self.enemies2 = self.enemies2, []

    def item_update(self):
        while len(self.items) > 0:
            item = self.items.pop()
            if item.name == "":
                continue
                # causes it to be removed on the next loop

            if self.player.get_rect().colliderect(item.get_rect()):
                if item.name == HEART:
                    self.player.hp += 2

                elif item.name == "container":
                    self.player.max_hp += 2
                    self.player.hp += 2
                    self.message("You have gotten a heart container!",
                        "Your life has increased by 2!")

                elif item.name == "seed":
                    self.player.seeds += 2

                elif item.name == "slingshot":
                    self.player.has_slingshot = True
                    
                    self.message("You have gotten a slingshot!",
                        "Press Z to shoot a seed!")

                elif item.name == "sword":
                    self.player.has_sword = True
                    self.message("You have gotten a sword!",
                        "Press X to slash,",
                        "or hold X to do a spin attack!")

                elif item.name == "pegasus":
                    self.player.has_pegasus = True
                    self.player.seeds = 5
                    self.message("You have gotten Pegasus Seeds!",
                        "Press A to increase your speed!")

                elif item.name == "triforce":
                    self.win()
                    # this is the part where you win 
                    #   △
                    #  △△
                item.name = ""
                ding.play()

            self.items2.append(item)
        self.items, self.items2 = self.items2, []


    def entity_update(self):
        while len(self.entities) > 0:
            entity = self.entities.pop()

            if not entity.move(entity.direction, entity.speed, self.world):
                if entity.bounce is not None:
                    entity.bounce += 1
                    if entity.bounce < 2:
                        entity.direction = reverse_direction(entity.direction)
                    else:
                        continue
                else:
                    continue

            # again, positive entity damage hurts player, negative hurts enemies
            if entity.damage > 0:
                if (self.player.get_rect().colliderect(entity.get_rect())
                      and not self.player.is_immune):
                    self.player.hurt(entity.damage, entity.direction, self.world)
                    continue

            elif entity.damage < 0:
                target = entity.get_rect().collidelist(self.enemy_rects)
                if target > -1:
                    if not self.enemies[target].is_immune:
                        self.enemies[target].move(24, entity.direction, self.world)
                        self.enemies[target].hp += entity.damage
                        self.enemies[target].immune = current_frame
                    continue

            self.entities2.append(entity)

        self.entities, self.entities2 = self.entities2, []

    # message handling
    def npc_update(self):
        for npc in self.world.npcs[(self.world.x, self.world.y)]:
            if self.player.get_rect(self.player.direction).colliderect(npc.get_rect()):
                self.message(*npc.messages)
                return       

    def check(self):
        # manages player health
        if self.player.hp > self.player.max_hp:
            self.player.hp = self.player.max_hp
        if self.player.hp <= 0:
            self.die()


    def map_blit(self):
        self.screen.blit(self.world.image, (0, 0),
        area=(self.world.x * 1280, self.world.y * 1024, 1280, 1024))

    def player_blit(self):
        self.screen.blit(self.player.current_sprite,
                        self.player.blit_location)

    def enemy_blit(self):
        for enemy in self.enemies:
            if enemy.state != DEAD:
                self.screen.blit(enemy.current_sprite,
                                 enemy.location)

    def item_blit(self):
        for item in self.items:
                self.screen.blit(item.current_sprite, item.location)

    def entity_blit(self):
        for entity in self.entities:
            self.screen.blit(entity.current_sprite, entity.location)

    def menu_blit(self):
        screen = self.screen
        # HP Bar
        draw.rect(screen, (0,  0,  0), (960, 0, 320, 36))
        draw.rect(screen, (255, 255, 255), (964, 4, 312, 28))
        draw.rect(screen, (255, 0, 0), (968, 8, 304, 20))
        draw.rect(screen, (0, 255, 0), (968, 8, (self.player.hp/self.player.max_hp) * 304, 20))

        if key.get_pressed()[K_LSHIFT]:
            # so it doesn't get in the way all of the time
            # hp bar always shows though
            if self.player.has_sword:
                draw.rect(screen, (0, 0, 0), (896, 0, 64, 64))
                screen.blit(sword_sprite, (896, 0))

            if self.player.has_slingshot:
                draw.rect(screen, (0, 0, 0), (832, 0, 64, 64))
                screen.blit(slingshot_sprite, (832, 0))
                

            if self.player.has_pegasus:
                draw.rect(screen, (0, 0, 0), (768, 0, 64, 64))
                screen.blit(pegasus_sprite, (768, 0))
                screen.blit(smallfont.render(str(self.player.seeds), False, (255, 255, 255)), (816, 48))

    def fps_blit(self):
        if self.fps_clock.get_time() > 0 and self.debug:
            fps = str(1000 // self.fps_clock.get_time())
            self.screen.blit(bigfont.render(fps, False, (255, 0, 0)), (0, 0))

    def message(self, *args):
        #args = [bigfont.render(x, False, (255, 255, 255)) for x in args]

        counter = 0

        beep.play()
        for i in range(len(args[counter])):
            self.screen.fill((  0,   0,   0), (0, 0, 1280, 96))
            self.screen.fill((255, 255, 255), (4, 4, 1272, 88))
            self.screen.fill((  0,   0,   0), (8, 8, 1264, 80))
            self.screen.blit(
                bigfont.render(args[counter][:i], False, (255, 255, 255)),
                (16, 16))
            sleep(0.02)
            display.flip()
        beep.stop()

        while True:
            for ev in event.get():
                if ev.type == QUIT:
                    raise SystemExit
                elif ev.type == KEYDOWN:
                    if ev.key == K_x:
                        counter += 1
                        if counter < len(args):
                            beep.play()
                            for i in range(len(args[counter])):
                                self.screen.fill((  0,   0,   0), (0, 0, 1280, 96))
                                self.screen.fill((255, 255, 255), (4, 4, 1272, 88))
                                self.screen.fill((  0,   0,   0), (8, 8, 1264, 80))
                                self.screen.blit(
                                    bigfont.render(args[counter][:i], False, (255, 255, 255)),
                                    (16, 16))
                                sleep(0.02)
                                display.flip()
                            beep.stop()


            if counter < len(args):
                self.screen.fill((  0,   0,   0), (0, 0, 1280, 96))
                self.screen.fill((255, 255, 255), (4, 4, 1272, 88))
                self.screen.fill((  0,   0,   0), (8, 8, 1264, 80))
                self.screen.blit(
                    bigfont.render(args[counter], False, (255, 255, 255)),
                    (16, 16))
            else:
                return 0

            display.flip()

    def win(self):
        mixer.music.stop()
        screen = self.screen
        x = Surface((1280, 1024))
        x.set_alpha(1)
        shaking_sound.play()
        for i in range(300):
            screen.blit(x, (0, 0))
            # scoring is just based on speed
            # I considered adding a no-item achievement, but I tried it myself
            # and nobody's beating this game without a sword
            screen.blit(bigfont.render("You won in " + str(current_frame//60) + " seconds!", False, (255, 255, 255)), (300, 500))
            sleep(0.01)
            display.flip()
            
        screen.fill((0, 0, 0))
        tele_sound.play()
        display.flip()

        running = True

        credits = image.load("credits.png")

        y = 640

        fps_clock = time.Clock()

        while running:
            for ev in event.get():
                if ev.type == QUIT:
                    quit()
                    raise SystemExit

            # moves the credits up each time
            y -= 2

            if y == 500:
                win_sound.play()

            screen.blit(credits, (0, y))
            display.flip()
            fps_clock.tick(100)


    def die(self):
        mixer.music.stop()
        screen = self.screen
        x = Surface((1280, 1024))
        x.set_alpha(1)
        pdead_sound.play()

        for i in range(300):
            screen.blit(x, (0, 0))
            sleep(0.01)
            display.flip()
        screen.fill((0, 0, 0))
        display.flip()

        running = True
        fps_clock = time.Clock()

        gameover_sound.play()

        gameover = image.load("gameover.png")
        gameover.set_alpha(1)

        while running:
            for ev in event.get():
                if ev.type == QUIT:
                    quit()
                    raise SystemExit

            screen.blit(gameover, (0, 0))

            display.flip()
            fps_clock.tick(150)


def main():
    Game()

if __name__ == '__main__':
    main()
