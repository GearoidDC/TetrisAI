import pygame


class Button:
    def __init__(self, color, x, y, button_width, button_height, text='', value=0):
        self.color = color
        self.x = x
        self.y = y
        self.width = button_width
        self.height = button_height
        self.font = pygame.font.SysFont('Arial', 30)
        self.text = text
        self.value = value

    # Draws button to screen
    def draw(self, screen):
        # Draw border for button
        pygame.draw.rect(screen, (0, 0, 0), (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        # Draw button
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)
        # Write text for button
        text = self.font.render(self.text, 1, (0, 0, 0))
        screen.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Returns true if the cords passed are over the button
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True

        return False
