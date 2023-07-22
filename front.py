import pygame # TODO: add icon
import math
import itertools as it
from enum import Enum
from collections import namedtuple
from operator import attrgetter
from dataclasses import dataclass
from draw_utils import (
    draw_cursor,
    draw_help_screen,
    draw_credits_screen,
    draw_license_screen,
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
    wire,
    button
)

mode = namedtuple('mode', 'name char nw binding constructor')
modes = {
    'wire': mode('wire', 'w', 2, draw_wire, wire),
    'button': mode('button', 'b', 2, draw_button, button), #FIXME
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
    box: pygame.Rect = None

pygame.init()
pygame.font.init()
pygame.mouse.set_visible(False)
font = pygame.font.SysFont('couriernew', 12)
screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
draw_utils.screen = screen
clock = pygame.time.Clock()
running = True
runner = None
run_error = False
current_mode = modes['wire']
help_mode = False
is_cursor_locked = False
pos = (0, 0)

pygame.display.set_caption('XEDEC')

lc = []         # List of components
tp = []         # Temporary points

def get_sp():   # Significiant points
    return it.chain(it.chain.from_iterable(map(attrgetter('pins'), lc)), tp)

def get_pos():
    global is_cursor_locked
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
        is_cursor_locked = True
    pos = tuple(pos)
    return pos

def setup_run():
    backend_component.reset_class()
    for c in lc:
        c.bec = c.type.constructor(*map(hash, c.pins))      # bec = back end component

def run(from_scratch=True):
    global run_error
    if from_scratch: setup_run()
    for c in lamp.lamp_register.values():
        c.on = False
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
    pos = get_pos() if runner is None else _pos
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
                        if c.type.name == 'button' and c.box.collidepoint(pos):
                            c.bec.on = not c.bec.on
                            runner = run(False)

            case pygame.KEYUP:
                if event.key == 122 and event.mod == 64:    # ???
                    lc.pop()
                if event.key == 27:
                    tp = []
                for m in modes.values():
                    if event.unicode == m.char:
                        current_mode = m
                        break
                if event.unicode == ' ':
                    runner = run() if runner is None else None
                    if runner is None:
                        for c in lc:
                            c.bec = None
                if event.unicode == 'h':
                    help_mode = False if help_mode == 'help' else 'help'
                elif event.unicode == 'c':
                    help_mode = False if help_mode == 'credits' else 'credits'
                elif event.unicode == 'l':
                    help_mode = False if help_mode == 'license' else 'license'

    ht = font.render("Press [h] for help, [c] for credits, [l] for license", False, 'yellow')
    screen.blit(ht, (screen.get_width() - ht.get_width() - 10, screen.get_height() - ht.get_height() - 10))

    if runner is not None:
        try:
            next(runner)
        except StopIteration:
            runner = None

    for p in tp:
        pygame.draw.line(screen, 'yellow', p, pos)

    draw_cursor(pos, color='green' if is_cursor_locked else 'yellow')
    is_cursor_locked = False

    if len(tp) == current_mode.nw:
        lc.append(component(current_mode, tp))
        run_error = False
        tp = []

    for c in lc:
        c.type.binding(*c.pins, component=c)

    if not help_mode:
        screen.blit(font.render(f"Mode: {current_mode.name}", False, 'yellow'), (0, 0))

        if runner is not None:
            run_error = False
            screen.blit(font.render("RUNNING", False, 'lightblue'), (0, 12))
        elif run_error:
            screen.blit(font.render("COULD NOT RUN", False, 'red'), (0, 12))
    elif help_mode == 'help':
        draw_help_screen((0, 0), font)
    elif help_mode == 'license':
        draw_license_screen((0, 0), font)
    elif help_mode == 'credits':
        draw_credits_screen((0, 0), font)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
