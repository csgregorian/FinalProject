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