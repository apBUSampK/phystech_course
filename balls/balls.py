import pygame
from pygame.draw import *
from random import randint, random
from pygame.font import *
from math import trunc

#pygame-related constants
FPS = 60
WINDOW_SIZE = (1200, 900)

#game-related constants
FRAMES_TO_SPAWN = 30
SPAWN_NUMBER = 1
MAX_BALLS = 8
MAX_SPEED = 100
POINT_CONST = 500

#game-related global variables
points = 0

#colors tuple
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
    '''
    A class for storing info about an individual ball, moving and drawing it
    '''
    def __init__(self):
        self.r = randint(10, 100)
        self.x = randint(self.r, 1200 - self.r)
        self.y = randint(self.r, 900 - self.r)
        self.vx = random() * MAX_SPEED
        self.vy = random() * MAX_SPEED
        self.color = COLORS[randint(0, 5)]
        self.clicked = False
    def draw(self):
        circle(screen, self.color, (self.x, self.y), self.r)
        circle(screen, BLACK, (self.x, self.y), self.r, width = 2)
    def move(self):
        if self.x - self.r <= 0 or self.x + self.r >= WINDOW_SIZE[0]:
            self.vx = -self.vx
        if self.y - self.r <= 0 or self.y + self.r >= WINDOW_SIZE[1]:
            self.vy = -self.vy
        self.x += self.vx/FPS
        self.y += self.vy/FPS
        
class Balls_list:
    '''
    A class for organizing info about multiple balls with update() method
    that is called every frame and add_ball() method for creating new balls
    '''
    def __init__(self):
        self.balls_list = []
    def add_ball(self):
        self.balls_list.append(Ball())
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
    '''
    A method for handling MOUSEBUTTONDOWN events
    '''
    global points
    if (((event.pos[0] - ball.x)**2 + (event.pos[1] - ball.y)**2)**0.5 <= ball.r):
        ball.clicked = True
        points += POINT_CONST/ball.r

#initialize pygame and screen surface
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.update()

#initialize other variables
balls = Balls_list()
text = SysFont('freesans', 128)
clock = pygame.time.Clock()
finished = False
counter = 0

#main loop
while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for ball in balls.balls_list:
                mouse_click(event, ball)
    if (counter > 0):
        counter -= 1
    else:
        for i in range(SPAWN_NUMBER):
            if balls.get_count() <= MAX_BALLS:
                balls.add_ball()
        counter = FRAMES_TO_SPAWN - 1
    screen.fill(WHITE)
    balls.update()
    screen.blit(text.render(str(trunc(points)), True, BLACK), (0, 0))
    pygame.display.update()

  
pygame.quit()
