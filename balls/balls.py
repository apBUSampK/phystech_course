import pygame
from random import randint, random
from pygame.font import *
from math import trunc

# pygame-related constants
FPS = 60
WINDOW_SIZE = (1200, 900)

# game-related constants
FRAMES_TO_SPAWN = 30
SPAWN_NUMBER = 1
MAX_OBJECTS = 8
MAX_SPEED = 100
POINT_CONST = 500
MAX_AMMO = 10
LEADERBOARD_POS = 10

# colors tuple
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]


class MutFloat:
    """
    A class for mutable float (I don't like global keyword)
    """
    def __init__(self, val):
        self.val = val


class Ball:
    """
    A class for storing info about an individual ball, moving and drawing it
    """

    def __init__(self, surface, rLowlim=10.0, rUplim=100.0, color=None):
        self.surface = surface
        self.r = random() * (rUplim - rLowlim) + rLowlim
        self.x = random() * (surface.get_width() - 2 * self.r) + self.r
        self.y = random() * (surface.get_height() - 2 * self.r) + self.r
        self.vx = random() * MAX_SPEED / FPS
        self.vy = random() * MAX_SPEED / FPS
        if color is None:
            self.color = COLORS[randint(0, 5)]
        else:
            self.color = color
        self.clicked = False

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.x, self.y), self.r)
        pygame.draw.circle(self.surface, BLACK, (self.x, self.y), self.r, width=2)

    def move(self):
        if self.x - self.r <= 0 or self.x + self.r >= self.surface.get_width():
            self.vx = -self.vx
        if self.y - self.r <= 0 or self.y + self.r >= self.surface.get_height():
            self.vy = -self.vy
        self.x += self.vx
        self.y += self.vy

    def check_click(self, x_click, y_click, score):
        if ((x_click - self.x) ** 2 + (y_click - self.y) ** 2) ** 0.5 <= self.r:
            self.clicked = True
            score.val += trunc(POINT_CONST / self.r)
            return True
        return False


class SqrTarget:
    """
    A class for a square target. The target contains a ball, bouncing inside it. On clicking the ball, points are gained,
    while on clicking the square itself, points are subtracted
    """
    def __init__(self, surface, sLowlim=50, sUplim=200):
        self.surface = surface
        self.side = randint(sLowlim, sUplim)
        self.x = randint(0, 1200 - self.side)
        self.y = randint(0, 900 - self.side)
        self.vx = random() * MAX_SPEED / FPS
        self.vy = random() * MAX_SPEED / FPS
        self.clicked = False
        self.ballSurface = pygame.Surface((self.side, self.side))
        self.ballSurface.fill(WHITE)
        self.ballSurface.set_colorkey(WHITE)
        self.ballTarget = Ball(self.ballSurface, rLowlim=10, rUplim=20 * self.side / sLowlim, color=GREEN)

    def draw(self):
        pygame.draw.rect(self.surface, RED, pygame.Rect(self.x, self.y, self.side, self.side))
        pygame.draw.rect(self.surface, BLACK, pygame.Rect(self.x, self.y, self.side, self.side), width=1)
        self.ballSurface.fill(WHITE)
        self.ballTarget.draw()
        self.surface.blit(self.ballSurface, (self.x, self.y))

    def move(self):
        if (self.x <= 0 and self.vx < 0) or (self.x + self.side >= self.surface.get_width()
                                                    and self.vx > 0):
            self.vx = -self.vx
        if (self.y <= 0 and self.vy < 0) or (self.y + self.side >= self.surface.get_height()
                                                    and self.vy > 0):
            self.vy = -self.vy
        self.x += self.vx
        self.y += self.vy
        self.ballTarget.move()

    def check_click(self, x_click, y_click, score):
        x_click -= self.x
        y_click -= self.y
        if 0 <= x_click <= self.side and 0 <= y_click <= self.side:
            if self.ballTarget.check_click(x_click, y_click, score):
                score.val += 3 * trunc(POINT_CONST / self.ballTarget.r)
            else:
                score.val -= trunc(POINT_CONST / 5 * self.ballTarget.r / self.side)
            self.clicked = True


class ObjList:
    """
    A class for organizing info about multiple objects with update() method
    that is called every frame and add_ball() method for creating new balls
    """

    def __init__(self, surface):
        self.obj_list = []
        self.surface = surface

    def add_ball(self):
        self.obj_list.append(Ball(self.surface))

    def add_sqr(self):
        self.obj_list.append(SqrTarget(self.surface))

    def update(self):
        for obj in self.obj_list:
            if obj.clicked:
                del self.obj_list[self.obj_list.index(obj)]
            else:
                obj.move()
                obj.draw()

    def get_count(self):
        return len(self.obj_list)

    def get_list(self):
        return self.obj_list


def game_over(surface, score):
    """
    A method for handling the leaderboard overwrite sequence at the end of the game
    :param surface: pygame.Surface object to draw in
    :param score: the score of current player
    :return: None
    """
    lines = 0
    index = 0
    _name_ = ""
    lb = SysFont('freesans', 46)
    lbB = SysFont('freesans', 128)
    surface.fill(WHITE)
    with open("leaderboard", mode='r') as f:
        prev_board = f.read().split('\n')
        f.seek(0)
        for line in f:
            pygame.draw.rect(surface, BLACK, pygame.Rect(100, 100 + lines * 50, 1000, 50), width=4)
            surface.blit(lb.render(line.split(' ')[0], True, BLACK), (110, 102 + lines * 50))
            surface.blit(lb.render(line.split(' ')[1][:-1], True, BLACK), (910, 102 + lines * 50))
            lines += 1
            if not index and score > int(line.split(' ')[1]):
                index = lines
    pygame.draw.rect(surface, BLACK, pygame.Rect(100, 100 + lines * 50, 1000, 50), width=4)
    pygame.draw.line(surface, BLACK, (900, 100), (900, 150 + lines * 50), width=4)
    surface.blit(lb.render(str(score), True, BLACK), (910, 102 + lines * 50))
    if index or lines < LEADERBOARD_POS:
        if not index:
            index = lines
        saved = False
        surface.blit(lb.render("Enter your name: " + _name_, True, BLACK),
                     (110, 102 + lines * 50))
        pygame.display.update()
        while not saved:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if pygame.K_SPACE <= event.key <= pygame.K_z:
                        _name_ += ' ' if pygame.key.name(event.key) == "space" else pygame.key.name(event.key)
                    if event.key == pygame.K_BACKSPACE:
                        _name_ = _name_[:-1]
                    pygame.draw.rect(surface, WHITE, pygame.Rect(100, 100 + lines * 50, 800, 50))
                    pygame.draw.rect(surface, BLACK, pygame.Rect(100, 100 + lines * 50, 800, 50), width=4)
                    surface.blit(lb.render("Enter your name: " + _name_, True, BLACK),
                                 (110, 102 + lines * 50))
                    pygame.display.update()
                    if event.key == pygame.K_RETURN and len(_name_) > 0:
                        with open("leaderboard", mode='w') as f:
                            for i in range(index - 1):
                                f.write(prev_board[i] + '\n')
                            f.write(_name_ + ' ' + str(score) + '\n')
                            for i in range(index - 1, min(lines, LEADERBOARD_POS)):
                                f.write(prev_board[i] + '\n')
                        surface.fill(WHITE)
                        surface.blit(lbB.render("Score saved!", True, BLACK), (250, 300))
                        pygame.display.update()
                        saved = True
                    if event.key == pygame.K_ESCAPE:
                        _name_ = _name_[:-1]
                        pygame.draw.rect(surface, WHITE, pygame.Rect(100, 100 + lines * 50, 800, 50))
                        pygame.draw.rect(surface, BLACK, pygame.Rect(100, 100 + lines * 50, 800, 50), width=4)
                        surface.blit(lb.render("Score save aborted!", True, BLACK), (110, 102 + lines * 50))
                        pygame.display.update()
                        saved = True
    else:
        surface.blit(lb.render("Your score is not high enough", True, BLACK), (100, 100 + lines * 50))
        pygame.display.update()

# initialize pygame and screen surface
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.update()

# initialize other variables
objects = ObjList(screen)
text = SysFont('freesans', 128)
clock = pygame.time.Clock()
finished = False
counter = 0
ammo = MAX_AMMO
points = MutFloat(0)

# main loop
while ammo and not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            ammo -= 1
            for obj in objects.get_list():
                obj.check_click(*event.pos, points)
    if counter > 0:
        counter -= 1
    else:
        for i in range(SPAWN_NUMBER):
            if objects.get_count() <= MAX_OBJECTS:
                if random() > 0.7:
                    objects.add_sqr()
                else:
                    objects.add_ball()
        counter = FRAMES_TO_SPAWN - 1
    screen.fill(WHITE)
    objects.update()
    screen.blit(text.render(str(points.val), True, BLACK), (0, 0))
    for x in range(0, ammo * 50, 50):
        screen.blit(pygame.image.load("shotgun shell.png"), (10 + x, 800))
    pygame.display.update()

if not finished:
    game_over(screen, points.val)

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True

pygame.quit()
