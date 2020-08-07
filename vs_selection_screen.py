import pygame
import sys
import button
import vs_mode
from settings import Setting

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width / 2
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width / 2

# Creating menu buttons
play_vs_cheater_ai_button = button.Button(button_colour_off, button_centred, 100,
                                          button_width, button_height, 'Play Vs Cheater AI')
play_vs_fair_ai_button = button.Button(button_colour_off, button_centred, 250,
                                       button_width, button_height, 'Play Vs Fair AI')
solo_cheater_ai_button = button.Button(button_colour_off, button_centred + 450, 100,
                                       150, button_height, 'Watch')
solo_fair_ai_button = button.Button(button_colour_off, button_centred + 450, 250,
                                    150, button_height, 'Watch')
return_button = button.Button(button_colour_off, button_centred, 400, button_width, button_height, 'Return')

# Array of Buttons
buttons = [play_vs_cheater_ai_button, play_vs_fair_ai_button, return_button, solo_fair_ai_button,
           solo_cheater_ai_button]


# Creates Vs Menu
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
                    go = vs_mode.start(screen, "cheater_tetris")
                elif play_vs_fair_ai_button.is_over(pos):
                    go = vs_mode.start(screen, "fair_tetris")
                elif solo_cheater_ai_button.is_over(pos):
                    go = vs_mode.start(screen, "cheater_tetris", "solo")
                elif solo_fair_ai_button.is_over(pos):
                    go = vs_mode.start(screen, "fair_tetris", "solo")
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
