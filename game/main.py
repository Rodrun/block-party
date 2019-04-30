# Single player offline game
import pygame
import json
from random import randint

from pygame.locals import *
from game.board import Board
from game.util import get_points, dimensions, resize


REPEAT = 60
TAS_REPEAT = 15

# System
pygame.init()
screen = pygame.display.set_mode([0, 0], pygame.NOFRAME)
screen_rect = screen.get_rect()
clock = pygame.time.Clock()
#pygame.key.set_repeat(60, REPEAT)
running = True

singleplayer = json.load(open("config/singleplayer.json"))
binds = singleplayer["binds"]

background = pygame.image.load("res/image/blue_background.png")

# Gameplay
config = json.load(open("config/standard.json"))
blocks = json.load(open("config/blocks.json", "r"))
block_data = blocks["blocks"]
block_cols = blocks["colors"]
level_speeds = json.load(open("config/frames.json", "r"))
font = pygame.font.Font("res/font/akashi.ttf",
    screen.get_height() // 15)
board = Board(screen_rect.width, screen_rect.height, config["board"],
    block_data, block_cols, level_speeds, font, "player1", None, None)

music_path = str(singleplayer["music"])
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)

fps = 60
while running:
    clock.tick(60)
    fps = clock.get_fps()
    if fps <= 0:
        fps = 60 # Should be this for 10 frames
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            else:
                for name, keycode in binds.items():
                    if event.key == keycode:
                        board.performInput(name)

    board.update(1 / fps)
    resize(background, pygame.display.get_surface().get_size())

    screen.blit(background, (0, 0), None, pygame.BLEND_RGBA_MAX)
    board.draw(screen)
    pygame.display.flip()
