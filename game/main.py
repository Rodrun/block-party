import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode([0, 0], pygame.NOFRAME)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.flip()
