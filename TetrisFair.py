import pygame
import random
import torch

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

    def __init__(self, screen, mode, draw):
        # GLOBALS VARS
        self.draw = draw
        self.mode = mode
        self.screen = screen
        # GLOBALS VARS
        self.s_width = 900
        self.s_height = 700

        self.distance_down = 0
        self.play_width = 300
        self.play_height = 600
        self.top_left_x = (self.s_width - self.play_width) // 5
        self.top_left_y = self.s_height - self.play_height - 10
        self.shapes = [self.S, self.Z, self.I, self.O, self.J, self.L, self.T]
        self.score = 0
        self.total_pieces_placed = 0
        self.total_lines_cleared = 0
        self.combo = 0
        self.max_combo = 0

        self.locked_positions = {}
        font = pygame.font.SysFont('comicsans', 60)
        self.label = font.render('AI Player', 1, (255, 255, 255))
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = self.get_shapes()
        self.change_piece = False
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.score = 0
        self.total_pieces_placed = 0
        self.run = True
        self.last_score = 0
        self.top_score = 0
        self.move = 0
        self.height = 20
        self.end_score = 0

    def create_grid(self):
        grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    c = self.locked_positions[(j, i)]
                    grid[i][j] = c
        return grid

    def convert_shape_format(self):
        positions = []
        shape_layout = self.current_piece.shape[self.current_piece.rotation % len(self.current_piece.shape)]

        for i, line in enumerate(shape_layout):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((self.current_piece.x + j, self.current_piece.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions

    def valid_space(self, grid):
        accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
        accepted_positions = [j for sub in accepted_positions for j in sub]
        formatted = self.convert_shape_format()

        for pos in formatted:
            if pos not in accepted_positions:
                if pos[1] > -1:
                    return False
                elif pos[0] > 9:
                    return False
                elif pos[0] < 0:
                    return False

        return True

    def check_lost(self):
        for pos in self.locked_positions:
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

    def draw_text_middle(self, text, size, color, surface):
        font = pygame.font.SysFont('comicsans', size, bold=True)
        label = font.render(text, 1, color)

        surface.blit(label, (self.s_width / 2 - (label.get_width() / 2), self.top_left_y - label.get_height() / 2))

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
                    grid = self.create_grid()
            else:
                i = i + 1
        return lines_cleared

    def cleared(self, grid):
        # need to see if row is clear the shift every other row above down one
        inc = 0
        array = []
        for i in range(len(grid) - 1, -1, -1):
            row = grid[i]
            if (0, 0, 0) not in row:
                # add positions to remove from locked
                array.append(i)
                inc += 1
                for j in range(len(row)):
                    grid[i][j] = (0, 0, 0)
        if inc > 0:
            for x in range(len(array) - 1, -1, -1):
                for i in range(array[x], 0, -1):
                    for j in range(len(grid[array[x]])):
                        grid[i][j] = grid[i - 1][j]
                        grid[i - 1][j] = (0, 0, 0)

        return inc, grid

    def bumpiness(self, grid):
        array_of_bump_heights = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
        average_bumps = 0
        height = 0

        # add piece to the grid for drawing
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] != (0, 0, 0) and i < array_of_bump_heights[j]:
                    array_of_bump_heights[j] = i

        for i in range(0, 9):
            average_bumps = average_bumps + abs(array_of_bump_heights[i] - array_of_bump_heights[i + 1])

        for i in range(0, 10):
            height = height + abs(array_of_bump_heights[i] - 20)
        return average_bumps, height

    def holes(self, grid):
        holes = 0
        average_height = 0
        for j in range(len(grid[0])):
            covered = False
            for i in range(len(grid)):
                if grid[i][j] == (0, 0, 0) and covered is True:
                    holes = holes + 1
                elif grid[i][j] != (0, 0, 0) and covered is False:
                    covered = True
                    average_height = average_height + i
        return holes

    def draw_next_shape(self, shape, surface, position):
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Next Shape', 1, (255, 255, 255))

        sx = position + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100
        shape_layout = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(shape_layout):
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

    # Tetris Title
    def draw_title(self, surface, label, position):
        surface.blit(label, (position + self.play_width / 2 - (label.get_width() / 2), 30))

    def draw_window(self, surface, position, grid, lines_sent):

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (position + j * 30, self.top_left_y + i * 30, 30, 30), 0)

        # draw grid and border
        self.draw_grid(surface, 20, 10, position)
        for line in range(lines_sent):
            pygame.draw.rect(surface, (0, 128, 128), (position - 40, 685 - line * 15, 20, 15), 0)
        self.draw_lines_sent(surface, 20, position)
        pygame.draw.rect(surface, (255, 0, 0), (position, self.top_left_y, self.play_width, self.play_height), 5)

    def get_state_properties(self, grid):
        lines_cleared, board = self.cleared(grid)
        holes = self.holes(board)
        bumpiness, height = self.bumpiness(board)

        return torch.FloatTensor([lines_cleared, holes, bumpiness, height, self.distance_down])

    def get_next_states(self):
        states = {}
        self.distance_down = 0
        normal = self.current_piece.x
        normal_y = self.current_piece.y
        normal_rotate = self.current_piece.rotation

        for j in range(4):
            grid_ai = self.create_grid()
            self.distance_down = 0
            valid = True
            x_move = 0
            if j == 1:
                while valid:
                    self.distance_down = 0
                    grid_ai = self.create_grid()
                    x_move += 1
                    self.current_piece.x -= x_move
                    if not self.valid_space(grid_ai):
                        self.current_piece.x = normal
                        valid = False
                    while self.valid_space(grid_ai):
                        self.current_piece.y += 1
                        self.distance_down += 1
                    self.current_piece.y -= 1
                    self.distance_down -= 1
                    if self.move == 2 and self.distance_down > 0:
                        self.distance_down -= 1
                    shape_pos = self.convert_shape_format()
                    # add piece to the grid for drawing
                    for i in range(len(shape_pos)):
                        x, y = shape_pos[i]
                        if y > -1:
                            grid_ai[y][x] = self.current_piece.color
                    if valid:
                        states[(j, x_move - 1)] = self.get_state_properties(grid_ai)
                    self.current_piece.x = normal
                    self.current_piece.y = normal_y
            if j == 2:
                while valid:
                    self.distance_down = 0
                    grid_ai = self.create_grid()
                    x_move += 1
                    self.current_piece.x += x_move
                    if not self.valid_space(grid_ai):
                        self.current_piece.x = normal
                        valid = False

                    while self.valid_space(grid_ai):
                        self.current_piece.y += 1
                        self.distance_down += 1
                    self.current_piece.y -= 1
                    self.distance_down -= 1
                    if self.move == 2 and self.distance_down > 0:
                        self.distance_down -= 1
                    shape_pos = self.convert_shape_format()
                    # add piece to the grid for drawing
                    for i in range(len(shape_pos)):
                        x, y = shape_pos[i]
                        if y > -1:
                            grid_ai[y][x] = self.current_piece.color
                    if valid:
                        states[(j, x_move - 1)] = self.get_state_properties(grid_ai)
                    self.current_piece.x = normal
                    self.current_piece.y = normal_y
            if j == 3:
                for z in range(4):
                    grid_ai = self.create_grid()
                    if z > 0 and valid:
                        self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                        if not self.valid_space(grid_ai):
                            self.current_piece.x -= 1
                            if not self.valid_space(grid_ai):
                                self.current_piece.x += 2
                                if not self.valid_space(grid_ai):
                                    self.current_piece.x += -1
                                    self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                                        self.current_piece.shape)
                                    valid = False
                        if valid:
                            while self.valid_space(grid_ai):
                                self.current_piece.y += 1
                                self.distance_down += 1
                            self.current_piece.y -= 1
                            self.distance_down -= 1
                            if self.move == 2 and self.distance_down > 0:
                                self.distance_down -= 1
                            shape_pos = self.convert_shape_format()
                            # add piece to the grid for drawing
                            for i in range(len(shape_pos)):
                                x, y = shape_pos[i]
                                if y > -1:
                                    grid_ai[y][x] = self.current_piece.color
                            if valid:
                                states[(j, z)] = self.get_state_properties(grid_ai)
                        self.current_piece.x = normal
                        self.current_piece.y = normal_y
                self.current_piece.rotation = normal_rotate
            if j == 0:
                while self.valid_space(grid_ai):
                    self.current_piece.y += 1
                self.current_piece.y -= 1
                shape_pos = self.convert_shape_format()
                # add piece to the grid for drawing
                for i in range(len(shape_pos)):
                    x, y = shape_pos[i]
                    if y > -1:
                        grid_ai[y][x] = self.current_piece.color
                states[(j, 0)] = self.get_state_properties(grid_ai)
                self.current_piece.y = normal_y
        return states

    def reset(self):

        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = self.get_shapes()
        self.change_piece = False
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.score = 0
        self.total_pieces_placed = 0
        self.run = False
        self.move = 0
        self.height = 20
        self.total_lines_cleared = 0
        self.end_score = 0
        self.combo = 0
        grid_ai = self.create_grid()
        return self.get_state_properties(grid_ai)

    def draw_stats(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont('comicsans', 30)

        label = font.render(f'Total Lines cleared = {self.total_lines_cleared}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 50))
        label = font.render(f'Pieces placed = {self.total_pieces_placed}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 20))
        label = font.render(f'Score = {self.score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 10))
        label = font.render(f'Max Combo = {self.max_combo}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 30))
        label = font.render(f'Last Score = {self.last_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 50))
        label = font.render(f'Top Score = {self.top_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 70))

    def step(self, action=[0, 0], lines_sent=0):
        area = pygame.Rect(self.top_left_x - 50, self.top_left_y, 550, 700)
        small_area = pygame.Rect(self.top_left_x - 50, self.top_left_y + 100, 400, 600)
        self.counter_human += lines_sent
        ai_move, num_rotations = action
        self.move = self.move + 1

        grid_ai = self.create_grid()
        if ai_move == 1:
            self.current_piece.x -= 1
            if not self.valid_space(grid_ai):
                self.current_piece.x += 1
        elif ai_move == 2:
            self.current_piece.x += 1
            if not self.valid_space(grid_ai):
                self.current_piece.x -= 1
        elif ai_move == 3:
            while num_rotations > 0:
                self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                if not self.valid_space(grid_ai):
                    self.current_piece.x -= 1
                    if not self.valid_space(grid_ai):
                        self.current_piece.x += 2
                        if not self.valid_space(grid_ai):
                            self.current_piece.x += -1
                            self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                                self.current_piece.shape)
                num_rotations -= 1
        if ai_move == 4:
            # move shape down
            self.current_piece.y += 1
            if not self.valid_space(grid_ai):
                self.current_piece.y -= 1
            else:
                self.move = 0

        if ai_move == 0:
            self.current_piece.y += 1
            if self.valid_space(grid_ai):
                while self.valid_space(grid_ai):
                    self.screen.fill((0, 0, 0), small_area)
                    shape_pos = self.convert_shape_format()
                    for i in range(len(shape_pos)):
                        x, y = shape_pos[i]
                        if y > -1:
                            grid_ai[y][x] = self.current_piece.color
                    self.draw_window(self.screen, self.top_left_x, grid_ai, self.counter_human)
                    pygame.display.update(small_area)
                    self.current_piece.y += 1
                    grid_ai = self.create_grid()
                else:
                    self.move = 0
                self.current_piece.y -= 1
            else:
                self.current_piece.y -= 1

        # PIECE FALLING CODE
        if self.move == 2:
            self.move = 0
            self.current_piece.y += 1
            if not (self.valid_space(grid_ai)) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                self.change_piece = True
        shape_pos = self.convert_shape_format()
        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid_ai[y][x] = self.current_piece.color
        # IF PIECE HIT GROUND
        lines_cleared = 0
        line_placed = 0
        if self.change_piece:
            self.current_piece.y += 1
            self.current_piece.y -= 1
            line_placed = 1
            self.total_pieces_placed += 1
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.height = pos[1]
                self.locked_positions[p] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = self.bag.pop()
            if not self.bag:
                self.bag = self.get_shapes()
            self.change_piece = False

            if self.check_lost():
                self.run = True

            if not self.run:
                self.counter_ai += self.clear_rows(grid_ai, self.locked_positions)
                self.score += self.counter_ai
                self.total_lines_cleared += self.counter_ai
                lines_cleared = self.counter_ai
                self.end_score = self.end_score + self.counter_ai ** 2
                self.counter_ai = 0
                if lines_cleared > self.counter_human:
                    lines_cleared = lines_cleared - self.counter_human
                elif lines_cleared == self.counter_human:
                    lines_cleared = 0
                    self.counter_human = 0
                elif lines_cleared < self.counter_human:
                    self.counter_human = self.counter_human - lines_cleared
                # Adds a row and moves rows up
                while self.counter_human > 0:
                    for j in range(10):
                        for i in range(20):
                            if (j, i) in self.locked_positions:
                                self.locked_positions[j, i - self.counter_human] = self.locked_positions[j, i]
                                del self.locked_positions[j, i]
                    lines_sent = random.sample(range(10), 9)
                    for x in range(self.counter_human):
                        for g in range(10):
                            self.locked_positions[g, 19 - x] = (0, 0, 0)
                    for x in range(self.counter_human):
                        for r in lines_sent:
                            self.locked_positions[r, 19 - x] = (169, 169, 169)
                    self.counter_human = 0

        if lines_cleared > 0:
            self.combo = (self.combo + 1)
        else:
            self.combo = 0
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        score = 1 * line_placed + (lines_cleared ** 2) * 10 + self.combo * 5
        self.score += score
        if self.run:
            self.last_score = self.score
            if self.top_score < self.score:
                self.top_score = self.score
        if self.draw:
            self.draw_stats()
        else:
            self.screen.fill((0, 0, 0), area)

        self.draw_window(self.screen, self.top_left_x, grid_ai, self.counter_human)
        self.draw_next_shape(self.next_piece, self.screen, self.top_left_x)
        self.draw_title(self.screen, self.label, self.top_left_x)
        if not self.draw:
            pygame.display.update(area)

        if self.mode == "train":
            out = score
        else:
            out = lines_cleared
        return out, self.run
