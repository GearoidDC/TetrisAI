import pygame
import copy
import torch
from TetrisModel import *
from TetrisAgent import *

pygame.font.init()


class Tetris:
    def __init__(self, screen, mode, draw):
        # GLOBALS VARS
        self.draw = draw
        self.mode = mode
        self.s_width = 900
        self.s_height = 700
        self.play_width = 300
        self.play_height = 600
        self.score = 0
        self.total_pieces_placed = 0
        self.total_lines_cleared = 0
        self.screen = screen
        self.locked_positions = {}
        font_header = pygame.font.SysFont('comicsans', 60)
        self.font_small = pygame.font.SysFont('comicsans', 30)
        self.label = font_header.render('AI Player', 1, (255, 255, 255))
        self.label_held_piece = self.font_small.render('Held Piece', 1, (255, 255, 255))
        self.label_next_piece = self.font_small.render('Next Piece', 1, (255, 255, 255))
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = get_shapes()
        self.change_piece = False
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.score = 0
        self.total_pieces_placed = 0
        self.run = False
        self.last_score = 0
        self.top_score = 0
        self.held_piece = []
        self.initial_grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

        self.combo = 0
        self.max_combo = 0

        self.top_left_x = (self.s_width - self.play_width) // 4
        self.top_left_y = self.s_height - self.play_height - 10
        draw_title(self.screen, self.label, self.top_left_x, self.play_width)

    def get_held_piece(self):
        if not self.held_piece:
            self.held_piece = self.current_piece
            self.current_piece = self.next_piece

            self.next_piece = self.bag.pop()
            if not self.bag:
                self.bag = get_shapes()
        else:
            holder = self.held_piece
            self.held_piece = self.current_piece
            self.current_piece = holder
        self.current_piece.y = self.held_piece.y
        self.current_piece.x = self.held_piece.x

    def swap_piece(self):
        if not self.held_piece:
            return copy.deepcopy(self.next_piece)
        else:
            return copy.deepcopy(self.held_piece)

    def draw_window(self, surface, position, grid, lines_sent):

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (position + j * 30, self.top_left_y + i * 30, 30, 30), 0)

        # draw grid and border
        draw_grid(surface, 20, 10, position, self.top_left_y, self.play_width, self.play_height)
        if not self.draw:
            for line in range(lines_sent):
                pygame.draw.rect(surface, (0, 128, 128), (position - 40, 685 - line * 15, 20, 15), 0)
            draw_lines_sent(surface, 20, position, self.top_left_y)
        pygame.draw.rect(surface, (255, 0, 0), (position, self.top_left_y, self.play_width, self.play_height), 5)

    def get_state_properties(self, grid):
        lines_cleared, board = cleared(grid)
        number_of_holes = holes(board)
        bumpiness, height = bumpiness_and_height(board)
        return torch.FloatTensor([lines_cleared, number_of_holes, bumpiness, height])

    def get_next_states(self):
        states = {}
        grid = create_grid(self.locked_positions)
        accepted_positions = self.locked_positions
        use_piece = copy.deepcopy(self.current_piece)
        cp = [row[:] for row in grid]
        for k in range(2):
            if k == 1:
                use_piece = self.swap_piece()
            normal_x = use_piece.x
            normal_y = use_piece.y
            normal_rotate = use_piece.rotation
            if use_piece.index < 3:
                rotates = 3
            elif use_piece.index > 3:
                rotates = 4
            else:
                rotates = 1
            for j in range(2):
                valid = True
                grid = [row[:] for row in cp]
                # checks all positions right with all rotations
                if j == 0:
                    for z in range(rotates):
                        x_move = 0
                        if z > 0:
                            use_piece.rotation = use_piece.rotation + 1 % len(use_piece.shape)
                        while valid:
                            use_piece.x += x_move
                            if not valid_space(use_piece, accepted_positions):
                                valid = False
                            if valid:
                                while valid_space(use_piece, accepted_positions):
                                    use_piece.y += 1
                                use_piece.y -= 1
                                shape_pos = convert_shape_format(use_piece)
                                # add piece to the grid for drawing
                                for i in range(len(shape_pos)):
                                    x, y = shape_pos[i]
                                    if y > -1:
                                        grid[y][x] = use_piece.color
                                states[(x_move, z, k)] = self.get_state_properties(grid)
                            use_piece.x = normal_x
                            use_piece.y = normal_y
                            grid = [row[:] for row in cp]
                            x_move += 1
                        valid = True
                    use_piece.rotation = normal_rotate
                # checks all positions right with all rotations
                elif j == 1:
                    for z in range(rotates):
                        x_move = 0
                        if z > 0:
                            use_piece.rotation = use_piece.rotation + 1 % len(use_piece.shape)
                        while valid:
                            x_move -= 1
                            use_piece.x += x_move
                            if not valid_space(use_piece, accepted_positions):
                                valid = False
                            if valid:
                                while valid_space(use_piece, accepted_positions):
                                    use_piece.y += 1
                                use_piece.y -= 1
                                shape_pos = convert_shape_format(use_piece)
                                # add piece to the grid for drawing
                                for i in range(len(shape_pos)):
                                    x, y = shape_pos[i]
                                    if y > -1:
                                        grid[y][x] = use_piece.color
                                states[(x_move, z, k)] = self.get_state_properties(grid)
                            use_piece.x = normal_x
                            use_piece.y = normal_y
                            grid = [row[:] for row in cp]
                        valid = True
                    use_piece.rotation = normal_rotate
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
        self.score = 0
        self.total_pieces_placed = 0
        self.run = False
        self.total_lines_cleared = 0
        self.combo = 0
        return self.get_state_properties(self.initial_grid)

    def draw_stats(self):
        area = pygame.Rect(0, 75, 800, 600)
        self.screen.fill((0, 0, 0), area)
        label = self.font_small.render(f'Total Lines cleared = {self.total_lines_cleared}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y))
        label = self.font_small.render(f'Pieces placed = {self.total_pieces_placed}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 20))
        label = self.font_small.render(f'Score = {self.score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 40))
        label = self.font_small.render(f'Max Combo = {self.max_combo}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 60))
        label = self.font_small.render(f'Last Score = {self.last_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 80))
        label = self.font_small.render(f'Top Score = {self.top_score}', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 100))

    def step(self, action=[0, -1, 0], lines_sent=0):
        self.counter_human += lines_sent
        ai_move, num_rotations, swap = action

        grid = create_grid(self.locked_positions)
        if swap == 1:
            self.get_held_piece()
        while num_rotations > 0:
            self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
            num_rotations = num_rotations - 1

        self.current_piece.x += ai_move
        accepted_positions = self.locked_positions
        while valid_space(self.current_piece, accepted_positions):
            self.current_piece.y += 1
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
                # call four times to check for multiple clear rows
                self.counter_ai += clear_rows(grid, self.locked_positions)
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
                    rows_to = random.sample(range(10), 9)
                    for x in range(self.counter_human):
                        for r in rows_to:
                            self.locked_positions[r, 19 - x] = (169, 169, 169)
                    self.counter_human = 0
        if lines_cleared > 0:
            self.combo = (self.combo + 1)
        else:
            self.combo = 0
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        score = 1 * line_placed + pow(lines_cleared, 2) * 10 + self.combo * 5
        self.score += score
        area = pygame.Rect(0, self.top_left_y, 650, 700)
        if self.run or (lines_sent == 1 and self.mode == "train"):
            self.last_score = self.score
            if self.top_score < self.score:
                self.top_score = self.score
        if self.draw:
            self.draw_stats()
        else:
            self.screen.fill((0, 0, 0), area)

        self.draw_window(self.screen, self.top_left_x, grid, self.counter_human)
        draw_next_shape(self.next_piece, self.screen, self.top_left_x, self.label_next_piece, self.top_left_y)
        draw_held_shape(self.held_piece, self.screen, self.top_left_x, self.label_held_piece, self.top_left_y)
        if not self.draw:
            pygame.display.update(area)

        if self.mode == "train":
            out = score
        else:
            out = lines_cleared
        return out, self.run
