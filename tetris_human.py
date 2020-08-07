from tetris_model import *


class Tetris:
    def __init__(self, screen):
        self.screen = screen
        self.s_width = 1400
        self.s_height = 700
        self.play_width = 300
        self.play_height = 600
        self.top_left_x = (self.s_width - self.play_width) // 1.3
        self.top_left_y = self.s_height - self.play_height - 10

        font = pygame.font.SysFont('Arial', 40)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.label = font.render('Human Player', 1, (255, 255, 255))
        self.label_held_piece = self.font_small.render('Held Piece', 1, (255, 255, 255))
        self.label_next_piece = self.font_small.render('Next Piece', 1, (255, 255, 255))

        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.bag = get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.combo = 0

        self.switch_piece = True
        self.change_piece = False
        self.run = False

        draw_title(self.screen, self.label, self.top_left_x, self.play_width)

    def get_held_piece(self):
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

    def reset(self):
        self.locked_positions = {}
        self.counter_ai = 0
        self.counter_human = 0
        self.combo = 0
        self.bag = get_shapes()
        self.current_piece = self.bag.pop()
        self.next_piece = self.bag.pop()
        self.held_piece = []
        self.switch_piece = True
        self.change_piece = False
        self.run = False

    # User controls
    def controls(self, movement):
        # Moves piece left
        accepted_positions = self.locked_positions
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

    def draw_screen(self, grid):
        area = pygame.Rect(self.top_left_x - 150, 75, 700, 625)
        self.screen.fill((0, 0, 0), area)
        draw_window(self.screen, self.top_left_x, grid, self.play_width, self.play_height, self.top_left_y)
        draw_lines_sent(self.screen, 20, self.top_left_x, self.top_left_y, self.counter_ai)
        draw_next_shape(self.next_piece, self.screen, self.top_left_x, self.label_next_piece, self.top_left_y)
        draw_held_shape(self.held_piece, self.screen, self.top_left_x, self.label_held_piece, self.top_left_y)
        pygame.display.update(area)

    def piece_falling(self):
        accepted_positions = self.locked_positions
        self.current_piece.y += 1
        if not (valid_space(self.current_piece, accepted_positions)) and self.current_piece.y > 0:
            self.current_piece.y -= 1
            return True
        return False

    def piece_landed(self):
        self.switch_piece = True
        shape_pos = convert_shape_format(self.current_piece)
        for pos in shape_pos:
            p = (pos[0], pos[1])
            self.locked_positions[p] = self.current_piece.color

        self.current_piece = self.next_piece
        self.next_piece = self.bag.pop()
        if not self.bag:
            self.bag = get_shapes()

    def get_score(self, grid):
        counter_human = 0
        counter_human += clear_rows(grid, self.locked_positions)
        # scoring system
        if counter_human > 0:
            self.combo = (self.combo + 1)
        else:
            self.combo = 0
        if self.combo > 1:
            counter_human = counter_human
        elif counter_human > 0:
            counter_human = counter_human - 1
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
            for r in lines_sent:
                self.locked_positions[r, 19] = (169, 169, 169)
        return counter_human

    def main(self, movement=0, lines=0):
        landed = False
        self.counter_ai += lines
        grid = create_grid(self.locked_positions)
        score = 0
        if movement == 0:
            landed = self.piece_falling()
        elif movement > 0:
            landed = self.controls(movement)

        shape_pos = convert_shape_format(self.current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = self.current_piece.color
        if landed:
            self.piece_landed()
            score = self.get_score(grid)

        self.draw_screen(grid)
        if check_lost(self.locked_positions):
            self.run = True
        return self.run, score
