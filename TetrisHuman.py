import pygame
import random

pygame.font.init()


class Piece(object):

    def __init__(self, column, row, shape, shapes):
        shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255),
                        (128, 0, 128)]
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


class Tetris:
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

    def __init__(self, screen):
        self.screen = screen
        self.s_width = 1400
        self.s_height = 700
        self.play_width = 300
        self.play_height = 600
        self.top_right_x = (self.s_width - self.play_width) // 1.3
        self.top_left_y = self.s_height - self.play_height - 10
        self.shapes = [self.S, self.Z, self.I, self.O, self.J, self.L, self.T]
        font = pygame.font.SysFont('comicsans', 60)
        self.label = font.render('Human Player', 1, (255, 255, 255))

        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = self.get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.change_piece = False
        self.run = False

    def create_grid(self):
        grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    c = self.locked_positions[(j, i)]
                    grid[i][j] = c
        return grid

    def convert_shape_format(self, shape):
        positions = []
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((shape.x + j, shape.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions

    def valid_space(self, shape, grid):
        accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
        accepted_positions = [j for sub in accepted_positions for j in sub]
        formatted = self.convert_shape_format(shape)

        for pos in formatted:
            if pos not in accepted_positions:
                if pos[1] > -1:
                    return False
                elif pos[0] > 9:
                    return False
                elif pos[0] < 0:
                    return False

        return True

    def check_lost(self, positions):
        for pos in positions:
            x, y = pos
            if y < 0:
                return True
        return False

    def get_shapes(self):

        bar = random.sample(range(0, 7), 7)
        bag = []
        for i in range(7):
            bag.append(Piece(5, 0, self.shapes[bar[i]], self.shapes))

        return bag

    def draw_grid(self, surface, row, col, sx):
        sy = self.top_left_y
        for i in range(row):
            pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * 30),
                             (sx + self.play_width, sy + i * 30))  # horizontal lines
            for j in range(col):
                pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy),
                                 (sx + j * 30, sy + self.play_height))  # vertical lines

    def clear_rows(self, grid, locked):
        # need to see if row is clear the shift every other row above down one
        linessss = 0
        i = 0
        while i < len(grid):
            row = grid[i]
            if (0, 0, 0) not in row:
                inc = 1
                linessss += 1
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
                    grid = self.create_grid()
            else:
                i = i + 1
        return linessss

    def draw_next_shape(self, shape, surface, position):
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Next Shape', 1, (255, 255, 255))

        sx = position + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_lines_sent(self, surface, col, sx):

        sy = self.top_left_y
        for i in range(col):
            pygame.draw.line(surface, (128, 128, 128), (sx - 40, sy + i * 15 + self.play_height / 2),
                             (sx - 20, sy + i * 15 + self.play_height / 2))  # horizontal lines

        pygame.draw.line(surface, (128, 128, 128), (sx - 40, sy + self.play_height / 2),
                         (sx - 40, sy + self.play_height))  # vertical lines
        pygame.draw.line(surface, (128, 128, 128), (sx - 20, sy + self.play_height / 2),
                         (sx - 20, sy + self.play_height))

    def draw_window(self, surface, label, position, grid, lines_sent):

        # Tetris Title

        surface.blit(label, (position + self.play_width / 2 - (label.get_width() / 2), 30))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (position + j * 30, self.top_left_y + i * 30, 30, 30), 0)

        # draw grid and border
        self.draw_grid(surface, 20, 10, position)
        for line in range(lines_sent):
            pygame.draw.rect(surface, (0, 128, 128), (position - 40, 685 - line * 15, 20, 15), 0)
        self.draw_lines_sent(surface, 20, position)
        pygame.draw.rect(surface, (255, 0, 0), (position, self.top_left_y, self.play_width, self.play_height), 5)

    def reset(self):
        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = self.get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.change_piece = False
        self.run = False

    # User controls
    def controls(self, movement, grid):
        # Moves piece left
        if movement == 1:
            self.current_piece.x -= 1
            if not self.valid_space(self.current_piece, grid):
                self.current_piece.x += 1
        # Moves piece right
        elif movement == 2:
            self.current_piece.x += 1
            if not self.valid_space(self.current_piece, grid):
                self.current_piece.x -= 1
        # Rotates piece and deals with wall kicks
        elif movement == 3:
            self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
            if not self.valid_space(self.current_piece, grid):
                self.current_piece.x -= 1
                if not self.valid_space(self.current_piece, grid):
                    self.current_piece.x += 2
                    if not self.valid_space(self.current_piece, grid):
                        self.current_piece.x += -1
                        self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                            self.current_piece.shape)
        # Moves piece down 1
        elif movement == 4:
            self.current_piece.y += 1
            if not self.valid_space(self.current_piece, grid):
                self.current_piece.y -= 1
                return True
        # Moves piece until down while in a valid spot
        elif movement == 5:
            if self.valid_space(self.current_piece, grid):
                while self.valid_space(self.current_piece, grid):
                    self.current_piece.y += 1
                self.current_piece.y -= 1
            else:
                return True
        return False

    def update_screen(self, grid):
        self.screen.fill((0, 0, 0), (self.top_right_x - 50, 0, 550, 700))
        self.draw_window(self.screen, self.label, self.top_right_x, grid, self.counter_ai)
        self.draw_next_shape(self.next_piece, self.screen, self.top_right_x)
        pygame.display.update(self.top_right_x, 0, 300, 700)

    def piece_falling(self, grid):
        self.current_piece.y += 1
        if not (self.valid_space(self.current_piece, grid)) and self.current_piece.y > 0:
            self.current_piece.y -= 1
            return True
        return False

    def piece_landed(self, grid):
        shape_pos = self.convert_shape_format(self.current_piece)
        counter_human = 0
        for pos in shape_pos:
            p = (pos[0], pos[1])
            self.locked_positions[p] = self.current_piece.color

        self.current_piece = self.next_piece
        self.next_piece = self.bag.pop()
        if not self.bag:
            self.bag = self.get_shapes()

        counter_human += self.clear_rows(grid, self.locked_positions)
        # Adds a row and moves rows down
        if self.counter_ai > counter_human:
            self.counter_ai = self.counter_ai - counter_human
        elif self.counter_ai == counter_human:
            self.counter_ai = 0
            counter_human = 0
        elif self.counter_ai < counter_human:
            self.counter_human = counter_human - self.counter_ai
        while self.counter_ai > 0:
            self.counter_ai = self.counter_ai - 1
            for j in range(10):
                for i in range(20):
                    if (j, i) in self.locked_positions:
                        self.locked_positions[j, i - 1] = self.locked_positions[j, i]
                        del self.locked_positions[j, i]
            lines_sent = random.sample(range(10), 9)
            for g in range(10):
                self.locked_positions[g, 19] = (0, 0, 0)
            for r in lines_sent:
                self.locked_positions[r, 19] = (169, 169, 169)
        return counter_human

    def main(self, movement=0, lines=0):
        landed = False
        self.counter_ai += lines
        grid = self.create_grid()
        lines_sent = 0
        if movement == 0:
            landed = self.piece_falling(grid)
        elif movement > 0:
            landed = self.controls(movement, grid)

        shape_pos = self.convert_shape_format(self.current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = self.current_piece.color
        if landed:
            lines_sent = self.piece_landed(grid)
        self.update_screen(grid)
        if self.check_lost(self.locked_positions):
            self.run = True
        return self.run, lines_sent
