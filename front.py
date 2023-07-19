import pygame
import math
import itertools as it
from enum import Enum
from collections import namedtuple
from operator import attrgetter
from draw_utils import (
    draw_wire,
    draw_lamp,
    draw_positive,
    draw_negative,
    draw_button
)
import draw_utils

component = namedtuple('component', 'type pins')
mode = namedtuple('mode', 'name char nw binding')
modes = {
    'wire': mode('wire', 'w', 2, draw_wire),
    'lamp': mode('lamp', 'e', 2, draw_lamp),
    'positive': mode('positive', 's', 1, draw_positive),
    'negative': mode('negative', 'g', 1, draw_negative),
    'transistor': mode('transistor', 't', 3, None)
}

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('couriernew', 12)
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
draw_utils.screen = screen
clock = pygame.time.Clock()
running = True
current_mode = modes['wire']
pos = (0, 0)

pygame.display.set_caption('Electric circuit simulator')

lc = []         # List of components
tp = []         # Temporary points

def get_sp():   # Significiant points
    return it.chain(it.chain.from_iterable(map(attrgetter('pins'), lc)), tp)

def get_pos():    # TODO: Maybe in snap points, make it easier to add straight lines
    _pos = pygame.mouse.get_pos()
    pos = _pos
    sp = list(get_sp())
    for p in sp:    # snap to points
        if math.sqrt((pos[0] - p[0])**2 + (pos[1] - p[1])**2) < 10:
            pos = p
            break
    pos = list(pos)     # For mutability
    for p in sp:    # snap to directions
        if abs(p[0] - pos[0]) < 10:
            pos[0] = p[0]
        elif abs(p[1] - pos[1]) < 10:
            pos[1] = p[1]
        else:
            continue
        pygame.draw.line(screen, 'forestgreen', pos, p)
    pos = tuple(pos)
    return pos

while running:
    screen.fill('black')
    _pos = pygame.mouse.get_pos()
    pos = get_pos()
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.MOUSEMOTION:
                pass
            case pygame.MOUSEBUTTONUP:
                tp.append(pos)

            case pygame.KEYUP:
                if event.key == 122 and event.mod == 64:    # ???
                    lc.pop()
                for m in modes.values():
                    if event.unicode == m.char:
                        current_mode = m
                        break

    for p in tp:
        pygame.draw.line(screen, 'yellow', p, pos)
    pygame.draw.circle(screen, 'green', pos, 10)

    if len(tp) == current_mode.nw:
        lc.append(component(current_mode, tp))
        tp = []

    for c in lc:
        c.type.binding(*c.pins)

    screen.blit(font.render(f"Mode: {current_mode.name}", False, 'yellow'), (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
