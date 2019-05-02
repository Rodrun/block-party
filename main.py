import json

import pygame
from pygame.locals import *

from game.board import Board
from game.component import render_text
from game import util


CONTROLLER_URL = "tinyurl.com/"

# Load in buffer configuration
# The buffer configuration is what the Java client writes to before
# Launching this script
try:
    buffer = json.load(open("buffer.json"))
    if not buffer["multiplayer"]:
        raise Exception("Single player mode")
    # System
    pygame.init()
    screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    winf = pygame.display.Info()
    screen_rect = pygame.Rect(0, 0, winf.current_w, winf.current_h)
    print(winf)
    clock = pygame.time.Clock()
    msg = "Connect to: " + str(buffer["ip"])

    # Configurations
    config = json.load(open("config/standard.json"))
    blocks = json.load(open("config/blocks.json", "r"))
    block_data = blocks["blocks"]
    block_cols = blocks["colors"]
    level_speeds = json.load(open("config/frames.json", "r"))
    font = pygame.font.Font("res/font/akashi.ttf",
        screen.get_height() // 15)

    # Boards
    BWIDTH = screen_rect.width // 2
    BHEIGHT = screen_rect.height
    b0 = Board(BWIDTH, BHEIGHT, config["board"],
        block_data, block_cols, level_speeds, font, "", None, None)
    b1 = Board(BWIDTH, BHEIGHT, config["board"],
        block_data, block_cols, level_speeds, font, "", None, None)

    # Prerender
    background = pygame.image.load("res/image/blue_background.png")
    background = util.resize(background, util.dimensions(screen_rect))
    msgsize = (screen_rect.width // 3, screen_rect.height // 7)
    ctrlmsg = render_text("Controller: " + CONTROLLER_URL, font)
    ctrlmsg = util.resize(ctrlmsg, msgsize)
    ipmsg = render_text(msg, font)
    ipmsg = util.resize(ipmsg, msgsize)

    if pygame.mixer.get_init():
        pygame.mixer.music.load("res/music/Dance_of_the_salty_boys.ogg")
        pygame.mixer.music.play(-1)

    running = True
    waiting = True # Wait state
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

        if not waiting:
            b0.update(1 / fps)
            b1.update(1 / fps)
            
            screen.blit(background, (0, 0), None, pygame.BLEND_RGBA_MAX)
            b0.draw(screen)
            b1.draw(screen)
        else:
            screen.blit(ctrlmsg, (0, 0))
            screen.blit(ipmsg, (0, ctrlmsg.get_height()))
        pygame.display.flip()
except Exception as err:
    print(err)
    # Any errors, just log and singelplayer
    import game.main
