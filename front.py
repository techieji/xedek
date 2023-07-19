import pygame
import math
import itertools as it
from enum import Enum
from collections import namedtuple
from operator import attrgetter

FONT = 'couriernew'

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def lerp_line(p1, p2, d):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    k = math.sqrt(d**2 / (dx**2 + dy**2))
    return (p1[0] + dx*k, p1[1] + dy*k)

def add_delta(p1, d):
    return (p1[0] + d[0], p1[1] + d[1])

def draw_wire(ip, ep, color='yellow'):
    pygame.draw.line(screen, color, ip, ep)

def draw_lamp(ip, ep, r=10):
    draw_wire(ip, ep)
    pos = midpoint(ip, ep)
    pygame.draw.circle(screen, 'black', pos, r)
    pygame.draw.circle(screen, 'yellow', pos, r, 1)
    pygame.draw.line(screen, 'yellow',
             lerp_line(pos, add_delta(pos, (1, 1)), r),
             lerp_line(pos, add_delta(pos, (-1, -1)), r))
    pygame.draw.line(screen, 'yellow',
            lerp_line(pos, add_delta(pos, (-1, 1)), r),
            lerp_line(pos, add_delta(pos, (1, -1)), r))

def draw_positive(p):    # FIXME: Offset same amount as ground
    pygame.draw.circle(screen, 'yellow', p, 10, 1)
    pygame.draw.line(screen, 'yellow', (p[0], p[1] - 5), (p[0], p[1] + 5))
    pygame.draw.line(screen, 'yellow', (p[0] - 5, p[1]), (p[0] + 5, p[1]))

def draw_negative(p):
    pygame.draw.line(screen, 'yellow', p, (p[0], p[1] + 4))
    pygame.draw.line(screen, 'yellow', (p[0] - 9, p[1] + 4), (p[0] + 9, p[1] + 4))
    pygame.draw.line(screen, 'yellow', (p[0] - 5, p[1] + 8), (p[0] + 4, p[1] + 8))
    pygame.draw.line(screen, 'yellow', (p[0] - 1, p[1] + 12), (p[0] + 1, p[1] + 12))

def draw_button(ip, ep):
    draw_wire(ip, ep)
    pos = midpoint(ip, ep)
    # s1 = 

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
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
