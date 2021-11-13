import math
from random import *

import pygame

MAXTARGETS = 10
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
    """
    Объект-снаряд, выпускаемый пушкой
    """
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
        self.live = 4 * FPS

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vy += g/FPS
        if (self.x - self.r <= 0 and self.vx < 0) or (self.x + self.r >= WIDTH and self.vx > 0):
            self.vx = -self.vx
            self.live -= FPS
        if (self.y - self.r <= 0 and self.vy < 0) or (self.y + self.r >= HEIGHT and self.vy > 0):
            self.vy = -self.vy
            self.live -= FPS
        self.x += self.vx
        self.y += self.vy

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
        if isinstance(obj, Tank):
            if -self.r <= self.x - obj.x <= obj.width + self.r and -self.r <= self.y - obj.y <= obj.height + self.r:
                return True
        elif isinstance(obj, Target):
            if (obj.x - self.x)**2 + (obj.y - self.y)**2 <= (obj.r + self.r)**2:
                return True
        return False


class Bomb(Ball):
    """
    Снаряды, выпускаемые целью-бомбардировщиком.
    """
    def __init__(self, screen: pygame.Surface, x, y):
        super().__init__(screen, x, y)
        self.vy = 60/FPS
        self.r = 8
        self.color = GREEN

    def move(self):
        self.vy += g/FPS
        self.y += self.vy

    def draw(self):
        super().draw()
        pygame.draw.circle(
            self.screen,
            BLACK,
            (self.x, self.y),
            self.r,
            width=2
        )


class Gun:

    def __init__(self, screen: pygame.Surface, x, y):
        self.screen = screen
        self.x = x
        self.y = y
        self.f2_power = 3/FPS
        self.f2_on = False
        self.an = 1
        self.color = GREY
        self.mouse_x = 0
        self.mouse_y = 0

    def fire2_start(self):
        self.f2_on = True

    def fire2_end(self):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, int(self.x + math.cos(self.an) * 50),  int(self.y - math.sin(self.an) * 50))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = -self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = False
        self.f2_power = 3
        self.color = GREY

    def targeting(self, event=None):
        """Прицеливание. Зависит от положения мыши."""
        if event is None:
            self.an = - math.atan2(self.mouse_y - self.y, self.mouse_x - self.x)
        else:
            self.an = - math.atan2(event.pos[1] - self.y, event.pos[0] - self.x)
            self.mouse_y = event.pos[1]
            self.mouse_x = event.pos[0]

    def draw(self):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x + 50 * math.cos(-self.an),
                                                                self.y + 50 * math.sin(-self.an)), width=10)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 20:
                self.f2_power += 1/4
        self.color = hex(int(RED * (self.f2_power - 3)/17 + GREY * (20 - self.f2_power)/17))


class Target:
    """
    Объект-цель
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.r = randint(10, 50)
        self.x = randint(self.r, WIDTH - self.r)
        self.y = randint(self.r, int(HEIGHT/4) - self.r)
        self.vx = randint(0, 60) / FPS
        self.vy = randint(0, 30) / FPS
        self.color = RED

    def move(self):
        if (self.y <= self.r and self.vy <= 0) or (self.y >= int(HEIGHT/4) - self.r and self.vy >= 0):
            self.vy = - self.vy
        if (self.x <= self.r and self.vx <= 0) or (self.x >= WIDTH - self.r and self.vx >= 0):
            self.vx = - self.vx
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        pygame.draw.circle(self.screen, RED, (self.x, self.y), self.r)
        pygame.draw.circle(self.screen, BLACK, (self.x, self.y), self.r, width=1)


class Bomber(Target):
    """
    Цель-бомбардировщик. Сбрасывает снаярды, при столкновении с которыми игра закончится.
    Частота выпускания снарядов зависит от скорости бомбардировщика.
    """
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.timer = round(2 * FPS/(1 + (self.vx**2 + self.vy**2)**0.5))

    def move(self):
        super().move()
        global bombs
        self.timer -= 1
        if self.timer <= 0:
            bombs.append(Bomb(self.screen, self.x, self.y))
            self.timer = round(2 * FPS / (1 + (self.vx ** 2 + self.vy ** 2) ** 0.5))

    def draw(self):
        pygame.draw.circle(self.screen, CYAN, (self.x, self.y), self.r)
        pygame.draw.circle(self.screen, BLACK, (self.x, self.y), self.r, width=1)


class Tank:
    """
    Объект, контроллируемый игроком. Включает в себя пушку
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.x = 50
        self.y = HEIGHT - 50
        self.power = 250/FPS
        self.speed = 0
        self.height = 30
        self.width = 50
        self.gun = Gun(screen, self.x + self.width/2, self.y)

    def move(self):
        self.x += self.speed
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        self.gun.x = self.x + self.width/2
        self.gun.targeting()

    def draw(self):
        pygame.draw.rect(self.screen, GREY, pygame.Rect((self.x, self.y, self.width, self.height)))
        self.gun.draw()

    def right(self):
        self.speed += self.power

    def left(self):
        self.speed -= self.power


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
points = 0
balls = []
targets = []
bombs = []
player = Tank(screen)
timer = SPAWN_TIME * FPS

clock = pygame.time.Clock()
finished = False
game_over = False

while not finished and not game_over:
    clock.tick(FPS)
    timer -= 1

    if timer <= 0:
        timer = SPAWN_TIME * FPS
        if len(targets) < MAXTARGETS:
            if random() < .5:
                targets.append(Target(screen))
            else:
                targets.append(Bomber(screen))

    screen.fill(WHITE)
    player.move()
    player.draw()
    for target in targets:
        target.move()
        target.draw()
    for b in balls:
        b.move()
        b.draw()
    for b in bombs:
        b.move()
        b.draw()
    screen.blit(pygame.font.SysFont('freesans', 72).render(str(points), True, BLACK), (20, 20))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player.gun.fire2_start()
        elif event.type == pygame.MOUSEBUTTONUP:
            player.gun.fire2_end()
        elif event.type == pygame.MOUSEMOTION:
            player.gun.targeting(event=event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.right()
            if event.key == pygame.K_LEFT:
                player.left()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                player.left()
            if event.key == pygame.K_LEFT:
                player.right()

    for b in balls:
        b.move()
        for target in targets:
            if b.hittest(target):
                if isinstance(target, Bomber):
                    points += 1
                else:
                    points += 3
                b.live = 0
                del targets[targets.index(target)]
        b.live -= 1
        if b.live <= 0:
            del balls[balls.index(b)]

    for b in bombs:
        b.move()
        if b.hittest(player):
            game_over = True

    player.gun.power_up()

if game_over:
    screen.fill(WHITE)
    screen.blit(pygame.font.SysFont('freesans', 72).render("Game over!", True, BLACK), (230, 240))
    screen.blit(pygame.font.SysFont('freesans', 36).render("You scored " + str(points) + " points!", True, BLACK), (250, 320))
    pygame.display.update()
    while not finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True

pygame.quit()
