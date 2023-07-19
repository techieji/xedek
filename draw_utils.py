import math
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


