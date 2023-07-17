import pygame
import math
import itertools as it
from enum import Enum

class ComponentMode(Enum):
    WIRE = 1
    LAMP = 2
    POSITIVE = 3
    NEGATIVE = 4

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True
pos = (0, 0)

l = []
points = []

while running:
    screen.fill('black')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            for p in it.chain.from_iterable(points):
                if math.sqrt((event.pos[0] - p[0])**2 + (event.pos[1] - p[1])**2) < 10:
                    pos = p
                    break
            else:
                pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            l.append(pos)

    if len(l) == 1:
        pygame.draw.line(screen, 'yellow', l[0], pos)
    pygame.draw.circle(screen, 'green', pos, 10)

    if len(l) == 2:
        points.append(l)
        l = []
    for p in points:
        pygame.draw.line(screen, 'yellow', *p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
