import pygame
import json
from pygame.locals import *
from game.playfield import PlayField, Step


pygame.init()
screen = pygame.display.set_mode([0, 0], pygame.NOFRAME)
running = True

playfield = PlayField(json.load(open("config/blocks.json", "r")), "T")
drop_ticks = 0
movement_performed = False
success = False
movement_vertical = False

BLOCK_HEIGHT = screen.get_height() / playfield.get_height()
BLOCK_WIDTH = BLOCK_HEIGHT

def step(step: Step, ignore_performed: bool = False):
    movement_performed = not ignore_performed
    movement_vertical = step.get_type() == "vertical"
    success = playfield.step(step)


while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                step(Step.rotate())
            elif event.key == pygame.K_LEFT:
                step(Step.horizontal(True))
            elif event.key == pygame.K_RIGHT:
                step(Step.horizontal(False))
            elif event.key == pygame.K_DOWN:
                step(Step.vertical())

    drop_ticks += 1
    if drop_ticks > 60:
        drop_ticks = 0
        step(Step.vertical())

    # Rendering
    screen.fill((0, 0, 0))
    view = playfield.get_view()
    screen.fill((255, 255, 255), pygame.Rect(0, 0,
        BLOCK_WIDTH * view.get_width(), BLOCK_HEIGHT * view.get_height()))
    for j in range(view.get_height()):
        for i in range(view.get_width()):
            if view.get_at(i, j) != 0:
                pygame.draw.rect(screen, (0, 255, 0),
                    pygame.Rect(i * BLOCK_WIDTH, j * BLOCK_HEIGHT, BLOCK_WIDTH,
                    BLOCK_HEIGHT))
    pygame.display.flip()
