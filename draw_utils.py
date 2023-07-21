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
        fore = 'black'
        back = 'yellow'
    else:
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

def draw_button(ip, ep, component=None):
    draw_wire(ip, ep)
    pos = midpoint(ip, ep)
    # s1 = 

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
Keybindings:
    h: show this [h]elp string
    w: [w]ire
    e: [e]mitter/lamp
    s: [s]ource
    g: [g]round
    """.strip()
    draw_text(text, p, font)

def draw_credits_screen(p, font):
    text = """
XEDEC: eXtensible Electronic DEsign Kit

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
