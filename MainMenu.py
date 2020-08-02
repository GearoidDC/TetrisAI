import pygame
import sys
import Button
import TrainingSelectionScreen
import VsSelectionScreen
import os
from Settings import Setting

pygame.init()

# Centres the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
size = settings.screen_width, settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width/2
screen = pygame.display.set_mode(size,pygame.DOUBLEBUF)
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width/2

# Creating menu buttons
train_ai_button = Button.Button(button_colour_off, button_centred, 100, button_width, button_height, 'Train AI')
play_vs_ai_button = Button.Button(button_colour_off, button_centred, 250, button_width, button_height, 'Play Vs AI')
quit_button = Button.Button(button_colour_off, button_centred, 400, button_width, button_height, 'Quit')

# Array of Buttons
buttons = [train_ai_button, play_vs_ai_button, quit_button]
pygame.display.set_caption("Tetris")
while True:
    # Creates responses to user inputs
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if train_ai_button.isover(pos):
                TrainingSelectionScreen.main()
            if play_vs_ai_button.isover(pos):
                VsSelectionScreen.main()
            if quit_button.isover(pos):
                sys.exit()
        if event.type == pygame.MOUSEMOTION:
            for x in range(len(buttons)):
                if buttons[x].isover(pos):
                    buttons[x].color = button_colour_on
                else:
                    buttons[x].color = button_colour_off
    # Refreshes screen and draws buttons
    screen.fill(dark_grey)
    for x in range(len(buttons)):
        buttons[x].draw(screen)
    pygame.display.update()
