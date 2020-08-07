class Setting:

    def __init__(self):
        self.screen_width = 1400
        self.screen_height = 700
        self.screen_colour = 71, 73, 74

        self.button_colour_on = 61, 97, 128
        self.button_colour_off = 147, 150, 153
        self.button_width = 400
        self.button_height = 100


class TetrisSettings:

    def __init__(self):
        import pygame
        self.board_width = 300
        self.board_height = 600
        self.font_header = pygame.font.SysFont('Arial', 40)
        self.button_colour_on = 61, 97, 128
        self.button_colour_off = 147, 150, 153
        self.button_width = 400
        self.button_height = 100
