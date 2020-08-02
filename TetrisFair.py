import pygame
import torch
from TetrisModel import *
from TetrisAgent import *


class Tetris:
    def __init__(self, screen, mode, draw):

        self.draw = draw
        self.mode = mode
        self.screen = screen
        self.s_width = 900
        self.s_height = 700
        self.distance_down = 0
        self.play_width = 300
        self.play_height = 600
        self.top_left_x = (self.s_width - self.play_width) // 4
        self.top_left_y = self.s_height - self.play_height - 10
        self.score = 0
        self.total_pieces_placed = 0
        self.total_lines_cleared = 0
        self.combo = 0
        self.max_combo = 0
        self.locked_positions = {}
        self.font_small = pygame.font.SysFont('comicsans', 30)
        font = pygame.font.SysFont('comicsans', 60)
        self.label = font.render('AI Player', 1, (255, 255, 255))
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = get_shapes()
        self.change_piece = False
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.switch_piece = True
        self.run = True
        self.last_score = 0
        self.top_score = 0
        self.move = 0
        self.x_move = 0
        self.area = pygame.Rect(self.top_left_x - 50, self.top_left_y, 550, 700)
        self.small_area = pygame.Rect(self.top_left_x - 50, self.top_left_y + 100, 400, 600)
        self.initial_grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    def get_held_piece(self):
        grid = create_grid(self.locked_positions)
        accepted_positions = get_accepted_positions(grid)
        if self.switch_piece:
            if not self.held_piece:
                self.held_piece = self.current_piece
                self.current_piece = self.next_piece
                self.current_piece.y = self.held_piece.y
                self.current_piece.x = self.held_piece.x
                if not valid_space(self.current_piece,accepted_positions):
                    self.current_piece.x -= 1
                    if not valid_space(self.current_piece,accepted_positions):
                        self.current_piece.x += 2
                        if not valid_space(self.current_piece,accepted_positions):
                            self.current_piece.x += -1
                            if not valid_space(self.current_piece,accepted_positions):
                                self.current_piece.y -= 1
                                if not valid_space(self.current_piece,accepted_positions):
                                    self.current_piece.y += 1
                                    self.next_piece = self.current_piece
                                    self.current_piece = self.held_piece
                                    self.held_piece = []
                                    return False
                self.next_piece = self.bag.pop()
                if not self.bag:
                    self.bag = get_shapes()
            else:
                holder = self.held_piece
                self.held_piece = self.current_piece
                self.current_piece = holder
                self.current_piece.y = self.held_piece.y
                self.current_piece.x = self.held_piece.x
                if not valid_space(self.current_piece,accepted_positions):
                    self.current_piece.x -= 1
                    if not valid_space(self.current_piece,accepted_positions):
                        self.current_piece.x += 2
                        if not valid_space(self.current_piece,accepted_positions):
                            self.current_piece.x += -1
                            if not valid_space(self.current_piece,accepted_positions):
                                self.current_piece.y -= 1
                                if not valid_space(self.current_piece,accepted_positions):
                                    self.current_piece.y += 1
                                    self.current_piece = self.held_piece
                                    self.held_piece = holder
                                    return False
        else:
            return False
        return True

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
                    grid = create_grid(self.locked_positions)
            else:
                i = i + 1
        return lines_cleared

    def draw_next_shape(self, shape, surface, position):
        label = self.font_small.render('Next Shape', 1, (255, 255, 255))

        sx = position + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100
        shape_layout = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(shape_layout):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_held_shape(self, shape, surface, position):
        label = self.font_small.render('Held Piece', 1, (255, 255, 255))

        sx = position - 150
        sy = self.top_left_y
        if shape:
            shape.rotation = 0
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
        lines_cleared, board = cleared(grid)
        number_of_holes = holes(board)
        bumpiness, height = bumpiness_and_height(board)

        return torch.FloatTensor([lines_cleared, number_of_holes, bumpiness, height])

    def get_next_states(self):
        states = {}

        number = 1
        grid = create_grid(self.locked_positions)
        accepted_positions = get_accepted_positions(grid)
        normalstart = self.current_piece.x
        normal_ystart = self.current_piece.y
        normal_rotatestart = self.current_piece.rotation
        if self.switch_piece:
            number = 2
        for k in range(number):
            if k == 1:
                if not self.get_held_piece():
                    k = 2
            if k < 2:
                self.distance_down = 0
                normal = self.current_piece.x
                normal_y = self.current_piece.y
                normal_rotate = self.current_piece.rotation
                for j in range(4):
                    grid = create_grid(self.locked_positions)
                    self.distance_down = 0
                    valid = True
                    self.x_move = 0
                    if j == 1:
                        while valid:
                            self.distance_down = 0
                            grid = create_grid(self.locked_positions)
                            self.x_move += 1
                            self.current_piece.x -= self.x_move
                            if not valid_space(self.current_piece,accepted_positions):
                                self.current_piece.x = normal
                                valid = False
                            while valid_space(self.current_piece,accepted_positions):
                                self.current_piece.y += 1
                                self.distance_down += 1
                            self.current_piece.y -= 1
                            self.distance_down -= 1
                            if self.move == 2 and self.distance_down > 0:
                                self.distance_down -= 1
                            shape_pos = convert_shape_format(self.current_piece)
                            # add piece to the grid for drawing
                            for i in range(len(shape_pos)):
                                x, y = shape_pos[i]
                                if y > -1:
                                    grid[y][x] = self.current_piece.color

                                states[(j, self.x_move - 1,k)] = self.get_state_properties(grid)
                            self.current_piece.x = normal
                            self.current_piece.y = normal_y
                    if j == 2:
                        while valid:
                            self.distance_down = 0
                            grid = create_grid(self.locked_positions)
                            self.x_move += 1
                            self.current_piece.x += self.x_move
                            if not valid_space(self.current_piece,accepted_positions):
                                self.current_piece.x = normal
                                valid = False

                            while valid_space(self.current_piece,accepted_positions):
                                self.current_piece.y += 1
                                self.distance_down += 1
                            self.current_piece.y -= 1
                            self.distance_down -= 1
                            if self.move == 2 and self.distance_down > 0:
                                self.distance_down -= 1
                            shape_pos = convert_shape_format(self.current_piece)
                            # add piece to the grid for drawing
                            for i in range(len(shape_pos)):
                                x, y = shape_pos[i]
                                if y > -1:
                                    grid[y][x] = self.current_piece.color
                            if valid:
                                states[(j, self.x_move - 1,k)] = self.get_state_properties(grid)
                            self.current_piece.x = normal
                            self.current_piece.y = normal_y
                    if j == 3:
                        for z in range(4):
                            grid = create_grid(self.locked_positions)
                            if z > 0 and valid:
                                self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                                if not valid_space(self.current_piece,accepted_positions):
                                    self.current_piece.x -= 1
                                    if not valid_space(self.current_piece,accepted_positions):
                                        self.current_piece.x += 2
                                        if not valid_space(self.current_piece,accepted_positions):
                                            self.current_piece.x += -1
                                            self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                                                self.current_piece.shape)
                                            valid = False
                                if valid:
                                    while valid_space(self.current_piece,accepted_positions):
                                        self.current_piece.y += 1
                                        self.distance_down += 1
                                    self.current_piece.y -= 1
                                    self.distance_down -= 1
                                    if self.move == 2 and self.distance_down > 0:
                                        self.distance_down -= 1
                                    shape_pos = convert_shape_format(self.current_piece)
                                    # add piece to the grid for drawing
                                    for i in range(len(shape_pos)):
                                        x, y = shape_pos[i]
                                        if y > -1:
                                            grid[y][x] = self.current_piece.color
                                    if valid:
                                        states[(j, z,k)] = self.get_state_properties(grid)
                                self.current_piece.x = normal
                                self.current_piece.y = normal_y
                        self.current_piece.rotation = normal_rotate
                    if j == 0:
                        while valid_space(self.current_piece,accepted_positions):
                            self.current_piece.y += 1
                        self.current_piece.y -= 1
                        shape_pos = convert_shape_format(self.current_piece)
                        # add piece to the grid for drawing
                        for i in range(len(shape_pos)):
                            x, y = shape_pos[i]
                            if y > -1:
                                grid[y][x] = self.current_piece.color
                        states[(j, 0,k)] = self.get_state_properties(grid)
                        self.current_piece.y = normal_y
                if k == 1:
                    self.get_held_piece()
                    self.current_piece.y = normal_ystart
                    self.current_piece.x = normalstart
                    self.current_piece.rotation = normal_rotatestart
        return states

    def reset(self):

        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = get_shapes()
        self.change_piece = False
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.switch_piece = True
        self.score = 0
        self.total_pieces_placed = 0
        self.run = False
        self.move = 0
        self.total_lines_cleared = 0
        self.combo = 0
        return self.get_state_properties(self.initial_grid)

    def draw_stats(self):
        self.screen.fill((0, 0, 0))

        label = self.font_small.render(f'Total Lines cleared = {self.total_lines_cleared}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 50))
        label = self.font_small.render(f'Pieces placed = {self.total_pieces_placed}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 20))
        label = self.font_small.render(f'Score = {self.score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 10))
        label = self.font_small.render(f'Max Combo = {self.max_combo}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 30))
        label = self.font_small.render(f'Last Score = {self.last_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 50))
        label = self.font_small.render(f'Top Score = {self.top_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 70))

    def step(self, action=[-1, -1,-1], lines_sent=0):

        self.counter_human += lines_sent
        ai_move, num_rotations, swap = action
        self.move = self.move + 1

        grid = create_grid(self.locked_positions)
        accepted_positions = get_accepted_positions(grid)

        # Actions Swap/Rotate/Move
        if swap == 1:
            self.get_held_piece()
            self.switch_piece = False
        if ai_move == 1:
            self.current_piece.x -= 1
            if not valid_space(self.current_piece,accepted_positions):
                self.current_piece.x += 1
        elif ai_move == 2:
            self.current_piece.x += 1
            if not valid_space(self.current_piece,accepted_positions):
                self.current_piece.x -= 1
        elif ai_move == 3:
            while num_rotations > 0:
                self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                if not valid_space(self.current_piece,accepted_positions):
                    self.current_piece.x -= 1
                    if not valid_space(self.current_piece,accepted_positions):
                        self.current_piece.x += 2
                        if not valid_space(self.current_piece,accepted_positions):
                            self.current_piece.x += -1
                            self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                                self.current_piece.shape)
                num_rotations -= 1
        if ai_move == 4:
            # move shape down
            self.current_piece.y += 1
            if not valid_space(self.current_piece,accepted_positions):
                self.current_piece.y -= 1
            else:
                self.move = 0

        if ai_move == 0:
            self.current_piece.y += 1
            self.move = 2
            if valid_space(self.current_piece,accepted_positions):
                while valid_space(self.current_piece,accepted_positions):
                    self.screen.fill((0, 0, 0), self.small_area)
                    shape_pos = convert_shape_format(self.current_piece)
                    for i in range(len(shape_pos)):
                        x, y = shape_pos[i]
                        if y > -1:
                            grid[y][x] = self.current_piece.color
                    self.draw_window(self.screen, self.top_left_x, grid, self.counter_human)
                    pygame.display.update(self.small_area)
                    self.current_piece.y += 1
                    grid = create_grid(self.locked_positions)
                #else:
                #    self.move = 0
                self.current_piece.y -= 1
            else:
                self.current_piece.y -= 1

        # PIECE FALLING CODE
        if self.move == 2:
            self.move = 0
            self.current_piece.y += 1
            if not (valid_space(self.current_piece,accepted_positions)) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                self.change_piece = True

        shape_pos = convert_shape_format(self.current_piece)
        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = self.current_piece.color
        # IF PIECE HIT GROUND
        lines_cleared = 0
        line_placed = 0
        if self.change_piece:
            self.switch_piece = True
            line_placed = 1
            self.total_pieces_placed += 1
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = self.bag.pop()
            if not self.bag:
                self.bag = get_shapes()
            self.change_piece = False

            if check_lost(self.locked_positions):
                self.run = True

            if not self.run:
                self.counter_ai += self.clear_rows(grid, self.locked_positions)
                self.score += self.counter_ai
                self.total_lines_cleared += self.counter_ai
                lines_cleared = self.counter_ai
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
            self.screen.fill((0, 0, 0), self.area)

        self.draw_window(self.screen, self.top_left_x, grid, self.counter_human)
        self.draw_next_shape(self.next_piece, self.screen, self.top_left_x)
        self.draw_title(self.screen, self.label, self.top_left_x)
        self.draw_held_shape(self.held_piece, self.screen, self.top_left_x)

        if not self.draw:
            pygame.display.update(self.area)

        if self.mode == "train":
            out = score
        else:
            out = lines_cleared

        return out, self.run
