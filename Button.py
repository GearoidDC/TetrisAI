import pygame


class Button:
    def __init__(self, color, x, y, button_width, button_height, text='',value=0):
        self.color = color
        self.x = x
        self.y = y
        self.width = button_width
        self.height = button_height
        self.font = pygame.font.SysFont('Arial', 30)
        self.text = text
        self.value = value

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            text = self.font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Returns true if the cords passed are over the button
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True

        return False
