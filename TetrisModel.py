import random
import pygame


# Creates a Tetris Piece object
class Piece(object):
    def __init__(self, column, row, index):
        # SHAPE FORMATS
        S = [['.....',
              '.....',
              '..00.',
              '.00..',
              '.....'],
             ['.....',
              '..0..',
              '..00.',
              '...0.',
              '.....']]

        Z = [['.....',
              '.....',
              '.00..',
              '..00.',
              '.....'],
             ['.....',
              '..0..',
              '.00..',
              '.0...',
              '.....']]

        I = [['..0..',
              '..0..',
              '..0..',
              '..0..',
              '.....'],
             ['.....',
              '0000.',
              '.....',
              '.....',
              '.....']]

        O = [['.....',
              '.....',
              '.00..',
              '.00..',
              '.....']]

        J = [['.....',
              '.0...',
              '.000.',
              '.....',
              '.....'],
             ['.....',
              '..00.',
              '..0..',
              '..0..',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '...0.',
              '.....'],
             ['.....',
              '..0..',
              '..0..',
              '.00..',
              '.....']]

        L = [['.....',
              '...0.',
              '.000.',
              '.....',
              '.....'],
             ['.....',
              '..0..',
              '..0..',
              '..00.',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '.0...',
              '.....'],
             ['.....',
              '.00..',
              '..0..',
              '..0..',
              '.....']]

        T = [['.....',
              '..0..',
              '.000.',
              '.....',
              '.....'],
             ['.....',
              '..0..',
              '..00.',
              '..0..',
              '.....'],
             ['.....',
              '.....',
              '.000.',
              '..0..',
              '.....'],
             ['.....',
              '..0..',
              '.00..',
              '..0..',
              '.....']]

        shapes = [S, Z, I, O, J, L, T]
        shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255),
                        (128, 0, 128)]
        self.x = column
        self.y = row
        self.shape = shapes[index]
        self.color = shape_colors[shapes.index(self.shape)]
        self.rotation = 0
        self.index = index


# Creates the tetris board grid
def create_grid(locked_positions):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


# Draw the grid
def draw_grid(surface, row, col, sx, sy, play_width, play_height):
    for i in range(row):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * 30),
                         (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy),
                             (sx + j * 30, sy + play_height))  # vertical lines


# Returns a shuffled seven piece bag
def get_shapes():
    mixed_numbers = random.sample(range(0, 7), 7)
    bag = []
    for i in mixed_numbers:
        bag.append(Piece(5, 0, i))
    return bag


# Converts the piece in a group of coordinates
def convert_shape_format(current_piece):
    positions = []
    shape_layout = current_piece.shape[current_piece.rotation % len(current_piece.shape)]

    for i, line in enumerate(shape_layout):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((current_piece.x + j, current_piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(current_piece, accepted_positions):
    formatted = convert_shape_format(current_piece)

    for pos in formatted:
        if pos[1] < -5:
            return False
        elif pos[0] > 9:
            return False
        elif pos[0] < 0:
            return False
        elif pos[1] > 19:
            return False
        elif pos in accepted_positions:
            return False

    return True


def draw_lines_sent(surface, col, sx, sy):
    play_height = 600
    for i in range(col):
        pygame.draw.line(surface, (128, 128, 128), (sx - 40, sy + i * 15 + play_height / 2),
                         (sx - 20, sy + i * 15 + play_height / 2))  # horizontal lines

    pygame.draw.line(surface, (128, 128, 128), (sx - 40, sy + play_height / 2),
                     (sx - 40, sy + play_height))  # vertical lines
    pygame.draw.line(surface, (128, 128, 128), (sx - 20, sy + play_height / 2),
                     (sx - 20, sy + play_height))


def check_lost(locked_positions):
    return any(v[1] < 0 for v in locked_positions)


def clear_rows(grid, locked):
    lines_cleared = 0
    i = 0
    while i < len(grid):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc = 1
            lines_cleared += 1
            # add positions to remove from locked
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
            if inc > 0:
                for key in sorted(list(locked), key=lambda z: z[1])[::-1]:
                    x, y = key
                    if y < ind:
                        new_key = (x, y + 1)
                        locked[new_key] = locked.pop(key)
                grid = create_grid(locked)
        else:
            i = i + 1
    return lines_cleared


def draw_held_shape(shape, surface, position, label, sy):
    sx = position - 150
    sy = sy + 40
    if shape:
        shape.rotation = 0
        shape_layout = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(shape_layout):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy - 30))


def draw_next_shape(shape, surface, position, label, top_left_y):
    sx = position + 300 + 50
    sy = top_left_y + 600 / 2 - 100
    shape_layout = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(shape_layout):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy - 30))


# Tetris Title
def draw_title(surface, label, position, game_width):
    surface.blit(label, (position + game_width / 2 - (label.get_width() / 2), 30))
