import pygame
import json
from random import randint
from pygame.locals import *
from game.playfield import PlayField, Step


pygame.init()
screen = pygame.display.set_mode([0, 0], pygame.NOFRAME)
running = True

playfield = PlayField(json.load(open("config/blocks.json", "r")), "I")
drop_ticks = 0
clear_state = False
flash_ticks = 0
flash_times = 0
filled_visibility = False

BLOCK_HEIGHT = screen.get_height() / playfield.get_height()
BLOCK_WIDTH = BLOCK_HEIGHT


def new_block():
    global drop_ticks
    global clear_state
    playfield.clear_filled_rows()
    playfield.spawn("I", multiplier=randint(1, 3))
    drop_ticks = 0
    clear_state = False


def do_step(step: Step):
    global drop_ticks
    global clear_state
    global flash_ticks
    global flash_times
    result = playfield.step(step)
    if result:
        if playfield.get_filled_rows() != []:
            flash_ticks = 0
            flash_times = 0
            drop_ticks = 0
            clear_state = True
        if not clear_state:
            new_block()


while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if not clear_state:
                if event.key == pygame.K_UP:
                    do_step(Step.rotate())
                if event.key == pygame.K_LEFT:
                    do_step(Step.horizontal(True))
                elif event.key == pygame.K_RIGHT:
                    do_step(Step.horizontal(False))
                if event.key == pygame.K_DOWN:
                    do_step(Step.vertical())

    if not clear_state:
        drop_ticks += 1
        if drop_ticks > 200:
            drop_ticks = 0
            do_step(Step.vertical())
    else:
        flash_ticks += 1
        if flash_ticks > 60:
            flash_times += 1
            filled_visibility = not filled_visibility # Toggle
            flash_ticks = 0
        if flash_times >= 4:
            clear_state = False
            filled_visibility = True
            new_block()

    # Rendering
    screen.fill((0, 0, 0))
    view = playfield.get_view()
    screen.fill((255, 255, 255), pygame.Rect(0, 0,
        BLOCK_WIDTH * view.get_width(), BLOCK_HEIGHT * view.get_height()))
    for j in range(view.get_height()):
        if clear_state and not filled_visibility and\
             j in playfield.get_filled_rows():
            continue # Skip row to make "invisible"
        for i in range(view.get_width()):
            value = view.get_at(i, j)
            if value != 0:
                color = [0, 0, 0]
                c_val = value - 1
                if c_val >= 0 and c_val < len(color):
                    color[c_val] += 255
                else:
                    color = [60, 85, 90]

                pygame.draw.rect(screen, color,
                    pygame.Rect(i * BLOCK_WIDTH, j * BLOCK_HEIGHT, BLOCK_WIDTH,
                    BLOCK_HEIGHT))
                #pygame.draw.rect(screen, (20, 240, 20),
                #    pygame.Rect(i * BLOCK_WIDTH + 3, j * BLOCK_HEIGHT + 3,
                #        BLOCK_WIDTH - 3, BLOCK_HEIGHT - 3))
    pygame.display.flip()
