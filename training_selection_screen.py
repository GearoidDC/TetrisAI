import pygame
import sys
import button
import training_mode
from settings import Setting

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width/2
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width/2

# Creating menu buttons
play_vs_cheater_ai_button = button.Button(button_colour_off, button_centred, 100,
                                          button_width, button_height, 'Train Cheater AI')
play_vs_fair_ai_button = button.Button(button_colour_off, button_centred, 250,
                                       button_width, button_height, 'Train Fair AI')
return_button = button.Button(button_colour_off, button_centred, 400, button_width, button_height, 'Return')

# Array of Buttons
buttons = [play_vs_cheater_ai_button, play_vs_fair_ai_button, return_button]


# Creates Training Menu
def main():
    pygame.display.set_caption("Tetris")
    screen = pygame.display.set_mode((screen_width, screen_height))
    go = True
    while go:
        # Creates responses to user inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_vs_cheater_ai_button.is_over(pos):
                    go = training_mode.main("cheater", 4)
                elif play_vs_fair_ai_button.is_over(pos):
                    go = training_mode.main("fair", 5)
                elif return_button.is_over(pos):
                    go = False
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
