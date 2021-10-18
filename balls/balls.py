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
MAX_BALLS = 8
MAX_SPEED = 100
POINT_CONST = 500
MAX_AMMO = 10
LEADERBOARD_POS = 10

# game-related global variables
points = 0

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


class Ball:
    """
    A class for storing info about an individual ball, moving and drawing it
    """

    def __init__(self, surface):
        self.r = randint(10, 100)
        self.x = randint(self.r, 1200 - self.r)
        self.y = randint(self.r, 900 - self.r)
        self.vx = random() * MAX_SPEED
        self.vy = random() * MAX_SPEED
        self.color = COLORS[randint(0, 5)]
        self.clicked = False
        self.surface = surface

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.x, self.y), self.r)
        pygame.draw.circle(self.surface, BLACK, (self.x, self.y), self.r, width=2)

    def move(self):
        if self.x - self.r <= 0 or self.x + self.r >= self.surface.get_width():
            self.vx = -self.vx
        if self.y - self.r <= 0 or self.y + self.r >= self.surface.get_height():
            self.vy = -self.vy
        self.x += self.vx / FPS
        self.y += self.vy / FPS


class BallsList:
    """
    A class for organizing info about multiple balls with update() method
    that is called every frame and add_ball() method for creating new balls
    """

    def __init__(self, surface):
        self.balls_list = []
        self.surface = surface

    def add_ball(self):
        self.balls_list.append(Ball(self.surface))

    def update(self):
        for ball in self.balls_list:
            if ball.clicked:
                del self.balls_list[self.balls_list.index(ball)]
            else:
                ball.move()
                ball.draw()

    def get_count(self):
        return len(self.balls_list)


def mouse_click(event, ball):
    """
    A method for handling MOUSEBUTTONDOWN events
    """
    global points, ammo
    if ((event.pos[0] - ball.x) ** 2 + (event.pos[1] - ball.y) ** 2) ** 0.5 <= ball.r:
        ball.clicked = True
        points += trunc(POINT_CONST / ball.r)


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
                        _name_ += pygame.key.name(event.key)
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
    else:
        surface.blit(lb.render("Your score is not high enough", True, BLACK), (100, 100 + lines * 50))
        pygame.display.update()

# initialize pygame and screen surface
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.update()

# initialize other variables
balls = BallsList(screen)
text = SysFont('freesans', 128)
clock = pygame.time.Clock()
finished = False
counter = 0
ammo = MAX_AMMO

# main loop
while ammo and not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            ammo -= 1
            for ball in balls.balls_list:
                mouse_click(event, ball)
    if counter > 0:
        counter -= 1
    else:
        for i in range(SPAWN_NUMBER):
            if balls.get_count() <= MAX_BALLS:
                balls.add_ball()
        counter = FRAMES_TO_SPAWN - 1
    screen.fill(WHITE)
    balls.update()
    screen.blit(text.render(str(points), True, BLACK), (0, 0))
    for x in range(0, ammo * 50, 50):
        screen.blit(pygame.image.load("shotgun shell.png"), (10 + x, 800))
    pygame.display.update()

game_over(screen, points)

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True

pygame.quit()
