import pygame
import math
import itertools as it
from enum import Enum
from collections import namedtuple
from operator import attrgetter
from dataclasses import dataclass
from draw_utils import (
    draw_wire,
    draw_lamp,
    draw_positive,
    draw_negative,
    draw_button
)
import draw_utils

from graph import DirectedGraph
from electric import (
    component as backend_component,
    get_all_paths_from_positive,
    propagate_current_step,
    terminal,
    lamp,
    wire
)

mode = namedtuple('mode', 'name char nw binding constructor')
modes = {
    'wire': mode('wire', 'w', 2, draw_wire, wire),
    'button': mode('button', 'b', 2, draw_wire, wire),
    'lamp': mode('lamp', 'e', 2, draw_lamp, lamp),
    'positive': mode('positive', 's', 1, draw_positive, lambda p: terminal(p, voltage=1)),
    'negative': mode('negative', 'g', 1, draw_negative, lambda p: terminal(p, voltage=0)),
    'transistor': mode('transistor', 't', 3, None, None)      # FIXME
}

@dataclass
class component:
    type: mode
    pins: list[tuple[int,int]]
    bec: backend_component = None

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('couriernew', 12)
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
draw_utils.screen = screen
clock = pygame.time.Clock()
running = True
runner = None
run_error = False
current_mode = modes['wire']
pos = (0, 0)

pygame.display.set_caption('Electric circuit simulator')

lc = []         # List of components
tp = []         # Temporary points

def get_sp():   # Significiant points
    return it.chain(it.chain.from_iterable(map(attrgetter('pins'), lc)), tp)

def get_pos():
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

def run():
    global run_error
    backend_component.reset_class()
    for c in lc:
        c.bec = c.type.constructor(*map(hash, c.pins))      # bec = back end component
    try:
        dg = get_all_paths_from_positive()
    except TypeError as e:
        run_error = True
        print(e)
        return
    while True:
        propagate_current_step(dg)
        yield
    
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
                if runner is None:
                    tp.append(pos)
                else:
                    for c in lc:
                        if c.type.name == 'button':
                            pass

            case pygame.KEYUP:
                if event.key == 122 and event.mod == 64:    # ???
                    lc.pop()
                for m in modes.values():
                    if event.unicode == m.char:
                        current_mode = m
                        break
                if event.unicode == ' ':
                    runner = run() if runner is None else None
                    if runner is None:
                        for c in lc:
                            c.bec = None

    if runner is not None:
        try:
            next(runner)
        except StopIteration:
            runner = None

    for p in tp:
        pygame.draw.line(screen, 'yellow', p, pos)
    pygame.draw.circle(screen, 'green', pos, 10)

    if len(tp) == current_mode.nw:
        lc.append(component(current_mode, tp))
        run_error = False
        tp = []

    for c in lc:
        c.type.binding(*c.pins, component=c)

    screen.blit(font.render(f"Mode: {current_mode.name}", False, 'yellow'), (0, 0))

    if runner is not None:
        run_error = False
        screen.blit(font.render("RUNNING", False, 'lightblue'), (0, 12))
    elif run_error:
        screen.blit(font.render("COULD NOT RUN", False, 'red'), (0, 12))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
