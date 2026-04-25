
# p0 = font.render("0", True, (0, 0, 0))
# surface.blit(p0, CornerPoints[0])

import pygame

pygame.init()
font = pygame.font.SysFont("simsunextg", 15)


def displayText(surface, f, text, color, x, y):
    surface.blit(f.render(text, True, color), (x,y))

