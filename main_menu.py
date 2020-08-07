import pygame
import sys
import button
import training_selection_screen
import vs_selection_screen
import os
from settings import Setting

pygame.init()
# Centres the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
size = settings.screen_width, settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width / 2
screen = pygame.display.set_mode(size)
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width / 2

# Creating menu buttons
train_ai_button = button.Button(button_colour_off, button_centred, 100, button_width, button_height, 'Train AI')
play_vs_ai_button = button.Button(button_colour_off, button_centred, 250, button_width, button_height, 'Play Vs AI')
quit_button = button.Button(button_colour_off, button_centred, 400, button_width, button_height, 'Quit')

# Array of Buttons
buttons = [train_ai_button, play_vs_ai_button, quit_button]

# Set the caption for the window
pygame.display.set_caption("Tetris")


def main():
    while True:
        # Creates responses to user inputs
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if train_ai_button.is_over(pos):
                    training_selection_screen.main()
                if play_vs_ai_button.is_over(pos):
                    vs_selection_screen.main()
                if quit_button.is_over(pos):
                    sys.exit()
            if event.type == pygame.MOUSEMOTION:
                for x in range(len(buttons)):
                    if buttons[x].is_over(pos):
                        buttons[x].color = button_colour_on
                    else:
                        buttons[x].color = button_colour_off
        # Refreshes screen and draws buttons
        screen.fill(dark_grey)
        for x in range(len(buttons)):
            buttons[x].draw(screen)
        pygame.display.update()


main()
