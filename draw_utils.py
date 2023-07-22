import math    # TODO: add black background in draw_text
import pygame

screen = None

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def lerp_line(p1, p2, d):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    k = math.sqrt(d**2 / (dx**2 + dy**2))
    return (p1[0] + dx*k, p1[1] + dy*k)

def add_delta(p1, d):
    return (p1[0] + d[0], p1[1] + d[1])

def draw_wire(ip, ep, color='yellow', component=None):
    pygame.draw.line(screen, color, ip, ep)

def draw_lamp(ip, ep, component, r=10):
    if (component.bec is not None) and component.bec.on:
        print('on', end='\r')
        fore = 'black'
        back = 'yellow'
    else:
        print('off', end='\r')
        fore = 'yellow'
        back = 'black'
    draw_wire(ip, ep)
    pos = midpoint(ip, ep)
    pygame.draw.circle(screen, back, pos, r)
    pygame.draw.circle(screen, fore, pos, r, 1)
    pygame.draw.line(screen, fore,
             lerp_line(pos, add_delta(pos, (1, 1)), r),
             lerp_line(pos, add_delta(pos, (-1, -1)), r))
    pygame.draw.line(screen, fore,
            lerp_line(pos, add_delta(pos, (-1, 1)), r),
            lerp_line(pos, add_delta(pos, (1, -1)), r))

def draw_positive(p, component=None):    # FIXME: Offset same amount as ground
    pygame.draw.circle(screen, 'yellow', p, 10, 1)
    pygame.draw.line(screen, 'yellow', (p[0], p[1] - 5), (p[0], p[1] + 5))
    pygame.draw.line(screen, 'yellow', (p[0] - 5, p[1]), (p[0] + 5, p[1]))

def draw_negative(p, component=None):
    pygame.draw.line(screen, 'yellow', p, (p[0], p[1] + 4))
    pygame.draw.line(screen, 'yellow', (p[0] - 9, p[1] + 4), (p[0] + 9, p[1] + 4))
    pygame.draw.line(screen, 'yellow', (p[0] - 5, p[1] + 8), (p[0] + 4, p[1] + 8))
    pygame.draw.line(screen, 'yellow', (p[0] - 1, p[1] + 12), (p[0] + 1, p[1] + 12))

def draw_button(ip, ep, component):
    pos = midpoint(ip, ep)
    component.box = pygame.Rect(pos[0] - 15, pos[1] - 15, 30, 30)
    s1 = (pos[0] - 10, pos[1])
    s2 = (pos[0] + 10, pos[1])
    pygame.draw.line(screen, 'yellow', ip, s1)
    pygame.draw.circle(screen, 'yellow', s1, 2)
    if component.bec is not None and component.bec.on:
        pygame.draw.line(screen, 'yellow', (s1[0], s1[1]), (s2[0], s2[1]))
        pygame.draw.line(screen, 'yellow', (pos[0], pos[1]), (pos[0], pos[1] - 10))
    else:
        pygame.draw.line(screen, 'yellow', (s1[0], s1[1] - 10), (s2[0], s2[1] - 10))
        pygame.draw.line(screen, 'yellow', (pos[0], pos[1] - 10), (pos[0], pos[1] - 20))
    pygame.draw.circle(screen, 'yellow', s2, 2)
    pygame.draw.line(screen, 'yellow', s2, ep)

def draw_cursor(p, color='yellow'):
    #pygame.draw.circle(screen, 'green', pos, 10)
    pygame.draw.line(screen, color, (p[0] + 4, p[1]), (p[0] - 4, p[1]))
    pygame.draw.line(screen, color, (p[0], p[1] + 4), (p[0], p[1] - 4))

    pygame.draw.line(screen, color, (p[0] + 8, p[1]), (p[0] + 16, p[1]))
    pygame.draw.line(screen, color, (p[0] - 8, p[1]), (p[0] - 16, p[1]))
    pygame.draw.line(screen, color, (p[0], p[1] + 8), (p[0], p[1] + 16))
    pygame.draw.line(screen, color, (p[0], p[1] - 8), (p[0], p[1] - 16))

def draw_text(text, p, font):
    c = p[1]
    for l in text.split('\n'):
        s = font.render(l, False, 'yellow')
        screen.blit(s, (p[0], c))
        c += s.get_height()

def draw_help_screen(p, font):
    text = """
Usage:
    On startup, you are in EDIT mode. Upon
    pressing SPACE, you are in RUN mode.
    In RUN mode, mouse snapping is disabled
    and buttons can be toggled.

Keybindings:
    h: show/hide this [h]elp message
    c: show/hide the [c]redits
    l: show/hide the [l]icense

    w: [w]ire
    e: [e]mitter/lamp
    s: [s]ource
    g: [g]round
    b: [b]utton

    Esc: cancel current component
    Space: start/stop simulation
    """.strip()
    draw_text(text, p, font)

def draw_credits_screen(p, font):
    text = """
XEDEK: eXtensible Electronic DEsign Kit

Created by:
    Pradhyum Rajasekar <drpradhyum2016@outlook.com>
    Aditya Bansal <adityabansal0805@gmail.com>
""".strip()
    draw_text(text, p, font)

def draw_license_screen(p, font):
    text = """
Copyright (c) 2023 Pradhyum Rajasekar and Aditya Bansal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
""".strip()
    draw_text(text, p, font)
