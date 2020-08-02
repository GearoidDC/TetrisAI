import pygame
import random
from TetrisModel import *


class Tetris:
    def __init__(self, screen):
        pygame.font.init()
        self.screen = screen
        self.s_width = 1400
        self.s_height = 700
        self.play_width = 300
        self.play_height = 600
        self.top_right_x = (self.s_width - self.play_width) // 1.3
        self.top_left_y = self.s_height - self.play_height - 10
        font = pygame.font.SysFont('comicsans', 60)
        self.label = font.render('Human Player', 1, (255, 255, 255))
        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.switch_piece = True
        self.change_piece = False
        self.run = False

    def get_held_piece(self):
        grid = create_grid(self.locked_positions)
        accepted_positions = get_accepted_positions(grid)
        if self.switch_piece:
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
                    grid = create_grid(self.locked_positions)
            else:
                i = i + 1
        return linessss

    def draw_next_shape(self, shape, surface, position):
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Next Piece', 1, (255, 255, 255))

        sx = position + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_held_shape(self, shape, surface, position):
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Held Piece', 1, (255, 255, 255))

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
        self.bag = get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.switch_piece = True
        self.change_piece = False
        self.run = False

    # User controls
    def controls(self, movement, grid):
        # Moves piece left
        accepted_positions = get_accepted_positions(grid)
        if movement == 1:
            self.current_piece.x -= 1
            if not valid_space(self.current_piece, accepted_positions):
                self.current_piece.x += 1
        # Moves piece right
        elif movement == 2:
            self.current_piece.x += 1
            if not valid_space(self.current_piece, accepted_positions):
                self.current_piece.x -= 1
        # Rotates piece and deals with wall kicks
        elif movement == 3:
            self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
            if not valid_space(self.current_piece, accepted_positions):
                self.current_piece.x -= 1
                if not valid_space(self.current_piece, accepted_positions):
                    self.current_piece.x += 2
                    if not valid_space(self.current_piece, accepted_positions):
                        self.current_piece.x += -1
                        self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                            self.current_piece.shape)
        # Moves piece down 1
        elif movement == 4:
            self.current_piece.y += 1
            if not valid_space(self.current_piece, accepted_positions):
                self.current_piece.y -= 1
                return True
        # Moves piece until down while in a valid spot
        elif movement == 5:
            if valid_space(self.current_piece, accepted_positions):
                while valid_space(self.current_piece, accepted_positions):
                    self.current_piece.y += 1
                self.current_piece.y -= 1
            else:
                return True
        elif movement == 6:
            self.get_held_piece()
            self.switch_piece = False
            if not valid_space(self.current_piece, accepted_positions):
                self.current_piece.x -= 1
                if not valid_space(self.current_piece, accepted_positions):
                    self.current_piece.x += 2
                    if not valid_space(self.current_piece, accepted_positions):
                        self.current_piece.x += -1
                        if not valid_space(self.current_piece, accepted_positions):
                            self.current_piece.y -= 1
                            if not valid_space(self.current_piece, accepted_positions):
                                self.current_piece.y += 1
                                self.switch_piece = True
                                self.get_held_piece()
        return False

    def update_screen(self, grid):
        self.screen.fill((0, 0, 0), (self.top_right_x - 150, 0, 650, 700))
        self.draw_window(self.screen, self.label, self.top_right_x, grid, self.counter_ai)
        self.draw_next_shape(self.next_piece, self.screen, self.top_right_x)
        self.draw_held_shape(self.held_piece, self.screen, self.top_right_x)
        pygame.display.update(self.top_right_x-50, 0, 350, 700)

    def piece_falling(self, grid):
        accepted_positions = get_accepted_positions(grid)
        self.current_piece.y += 1
        if not (valid_space(self.current_piece, accepted_positions)) and self.current_piece.y > 0:
            self.current_piece.y -= 1
            return True
        return False

    def piece_landed(self, grid):
        self.switch_piece = True
        shape_pos = convert_shape_format(self.current_piece)
        counter_human = 0
        for pos in shape_pos:
            p = (pos[0], pos[1])
            self.locked_positions[p] = self.current_piece.color

        self.current_piece = self.next_piece
        self.next_piece = self.bag.pop()
        if not self.bag:
            self.bag = get_shapes()

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
        grid = create_grid(self.locked_positions)
        lines_sent = 0
        if movement == 0:
            landed = self.piece_falling(grid)
        elif movement > 0:
            landed = self.controls(movement, grid)

        shape_pos = convert_shape_format(self.current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = self.current_piece.color
        if landed:
            lines_sent = self.piece_landed(grid)
        self.update_screen(grid)
        if check_lost(self.locked_positions):
            self.run = True
        return self.run, lines_sent
