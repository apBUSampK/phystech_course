import math
from random import *

import pygame

MAXTARGETS = 2
SPAWN_TIME = 1

FPS = 60
g = 10

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 15
        self.vx = 0/FPS
        self.vy = 0/FPS
        self.color = choice(GAME_COLORS)
        self.live = 5 * FPS

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vy -= g/FPS
        if (self.x - self.r <= 0 and self.vx < 0) or (self.x + self.r >= WIDTH and self.vx > 0):
            self.vx = -self.vx
        if (self.y - self.r <= 0 and self.vy < 0) or (self.y + self.r >= HEIGHT and self.vy > 0):
            self.vy = -self.vy
        self.x += self.vx
        self.y -= self.vy

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if isinstance(obj, Target):
            if (obj.x - self.x)**2 + (obj.y - self.y)**2 <= (obj.r + self.r)**2:
                return True
            else:
                return False
        else:
            return False


class Gun:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.f2_power = 3/FPS
        self.f2_on = False
        self.an = 1
        self.color = GREY

    def fire2_start(self):
        self.f2_on = True

    def fire2_end(self):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, int(50 + math.cos(self.an) * 50),  HEIGHT - int(50 + math.sin(self.an) * 50))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = False
        self.f2_power = 3

    def targeting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        self.an = - math.atan2(event.pos[1] - HEIGHT + 50, event.pos[0] - 50)

    def draw(self):
        pygame.draw.line(screen, self.color, (50, HEIGHT - 50), (50 * (1 + math.cos(-self.an)),
                                                                 HEIGHT - 50 + 50 * math.sin(-self.an)), width=10)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 20:
                self.f2_power += 1/4
            self.color = RED
        else:
            self.color = GREY


class Target:

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.r = randint(2, 200)
        self.x = randint(600, WIDTH - self.r)
        self.y = randint(100, HEIGHT - self.r)
        self.vy = randint(0, 30)/FPS
        self.color = RED

    def new_target(self):
        """ Инициализация новой цели. """
        self.r = randint(2, 50)
        self.x = randint(600, WIDTH - self.r)
        self.y = randint(100, HEIGHT - self.r)
        self.color = RED

    def move(self):
        if (self.y <= 2 * self.r and self.vy <= 0) or (self.y >= HEIGHT - 2 * self.r and self.vy >= 0):
            self.vy = - self.vy
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(self.screen, RED, (self.x, self.y), self.r)
        pygame.draw.circle(self.screen, BLACK, (self.x, self.y), self.r, width=1)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
points = 0
balls = []
targets = []
timer = SPAWN_TIME * FPS

clock = pygame.time.Clock()
gun = Gun(screen)
finished = False

while not finished:
    clock.tick(FPS)
    timer -= 1

    if timer <= 0:
        timer = SPAWN_TIME * FPS
        if len(targets) < MAXTARGETS:
            targets.append(Target(screen))

    screen.fill(WHITE)
    gun.draw()
    for b in balls:
        b.move()
        b.draw()
    for target in targets:
        target.move()
        target.draw()
    screen.blit(pygame.font.SysFont('freesans', 72).render(str(points), True, BLACK), (20, 20))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start()
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end()
        elif event.type == pygame.MOUSEMOTION:
            gun.targeting(event)

    for b in balls:
        b.move()
        for target in targets:
            if b.hittest(target):
                points += 1
                target.live = 0
                b.live = 0
                del targets[targets.index(target)]
        b.live -= 1
        if b.live <= 0:
            del balls[balls.index(b)]

    gun.power_up()

pygame.quit()
