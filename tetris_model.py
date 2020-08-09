import random
import pygame


# Creates a Tetris Piece object
class Piece(object):
    def __init__(self, column, row, index):
        # Piece formats
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
        green, red, cyan, yellow, orange, blue, purple = (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (
            255, 165, 0), (0, 0, 255), (128, 0, 128)

        shape_colors = [green, red, cyan, yellow, orange, blue, purple]
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
def draw_grid(surface, x_coord, y_coord, play_width, play_height):
    row = 20
    column = 10
    block_size = 30
    grey = (128, 128, 128)
    for i in range(row):
        pygame.draw.line(surface, grey, (x_coord, y_coord + i * block_size),
                         (x_coord + play_width, y_coord + i * block_size))  # horizontal lines
        for j in range(column):
            pygame.draw.line(surface, grey, (x_coord + j * block_size, y_coord),
                             (x_coord + j * block_size, y_coord + play_height))  # vertical lines


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


# Returns if the passed spaces are valid to move into
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


# Draws the lines sent by the opponent
def draw_lines_sent(surface, x_coord, y_coord, lines_sent):
    rows = 21
    play_height = 600
    cyan = (0, 128, 128)
    grey = (128, 128, 128)
    for line in range(lines_sent):
        pygame.draw.rect(surface, cyan, (x_coord - 40, 675 - line * 15, 20, 15), 0)
    for i in range(rows):
        pygame.draw.line(surface, grey, (x_coord - 40, y_coord + i * 15 + play_height / 2),
                         (x_coord - 20, y_coord + i * 15 + play_height / 2))  # horizontal lines

    pygame.draw.line(surface, grey, (x_coord - 40, y_coord + play_height / 2),
                     (x_coord - 40, y_coord + play_height))  # vertical lines
    pygame.draw.line(surface, grey, (x_coord - 20, y_coord + play_height / 2),
                     (x_coord - 20, y_coord + play_height))


# Returns if the game is lost
def check_lost(locked_positions):
    return any(coordinate[1] < 0 for coordinate in locked_positions)


# Returns how many rows are cleared and clears the lines
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


# Draws the basic board of the game
def draw_window(surface, position, grid, top_left_y):
    play_width, play_height = 300, 600
    block_size = 30
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (position + j * block_size, top_left_y + i * block_size, block_size,
                                                   block_size), 0)

    # draw grid and border
    draw_grid(surface, position, top_left_y, play_width, play_height)
    pygame.draw.rect(surface, (255, 0, 0), (position, top_left_y, play_width, play_height), 5)


# Draws the held shape on the screen
def draw_held_shape(shape, surface, x_coord, label, y_coord):
    offset_right = 150
    block_size = 30
    x_coord = x_coord - offset_right
    offset_down = 40
    y_coord = y_coord + offset_down
    if shape:
        shape.rotation = 0
        shape_layout = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(shape_layout):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (x_coord + j * block_size, y_coord + i * block_size,
                                                            block_size, block_size), 0)

    surface.blit(label, (x_coord + 10, y_coord - block_size))


# Draws next shape on the screen
def draw_next_shape(shape, surface, x_coord, label, y_coord):
    x_coord = x_coord + 350
    y_coord = y_coord + 200
    shape_layout = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(shape_layout):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (x_coord + j * 30, y_coord + i * 30, 30, 30), 0)

    surface.blit(label, (x_coord + 10, y_coord - 30))


# Draws the title for the board
def draw_title(surface, label, position):
    play_width = 300
    surface.blit(label, (position + play_width / 2 - (label.get_width() / 2), 30))
