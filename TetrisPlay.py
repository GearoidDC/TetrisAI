import pygame
import random
import Button

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3


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

    return_button = Button.Button((61, 97, 128), 575, 625, 200, 50, 'Return')
    global shapes, shape_colors
    shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
    shapes = [S, Z, I, O, J, L, T]
    # index 0 - 6 represent shape

    def __init__(self):
        # GLOBALS VARS
        self.s_width = 900
        self.s_height = 700
        self.play_width = 300  # meaning 300 // 10 = 30 width per block
        self.play_height = 600  # meaning 600 // 20 = 20 height per block
        self.block_size = 30
        self.shapes = [self.S, self.Z, self.I, self.O, self.J, self.L, self.T]
        self.score = 0

        self.top_left_x = (self.s_width - self.play_width) // 5
        self.top_left_y = self.s_height - self.play_height -10


    def create_grid(self, locked_positions={}):
        grid = [[(0,0,0) for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j,i) in locked_positions:
                    c = locked_positions[(j,i)]
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
        accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
        accepted_positions = [j for sub in accepted_positions for j in sub]
        formatted = self.convert_shape_format(shape)

        for pos in formatted:
            if pos not in accepted_positions:
                if pos[1] > -1:
                    return False

        return True


    def check_lost(self,positions):
        for pos in positions:
            x, y = pos
            if y < 0:
                return True
        return False


    def get_shapes(self):

        bar = random.sample(range(0, 7), 7)
        bag = []
        for i in range(7):
            bag.append(Piece(5, 0, self.shapes[bar[i]]))

        return bag


    def draw_text_middle(self,text, size, color, surface):
        font = pygame.font.SysFont('comicsans', size, bold=True)
        label = font.render(text, 1, color)

        surface.blit(label, (self.s_width/2 - (label.get_width() / 2), self.top_left_y - label.get_height()/2))


    def draw_grid(self,surface, row, col, sx):
        sy = self.top_left_y
        for i in range(row):
            pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + self.play_width, sy + i * 30))  # horizontal lines
            for j in range(col):
                pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + self.play_height))  # vertical lines


    def clear_rows(self,grid, locked):
        # need to see if row is clear the shift every other row above down one
        linessss = 0
        inc = 0
        for i in range(len(grid)-1,-1,-1):
            row = grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                # add positions to remove from locked
                ind = i
                for j in range(len(row)):
                    try:
                        del locked[(j, i)]
                    except:
                        continue
        if inc > 0:
            linessss = inc
            print(inc)
            for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < ind:
                    newKey = (x, y + inc)
                    locked[newKey] = locked.pop(key)
        return linessss


    def draw_next_shape(self,shape, surface,position):
        font = pygame.font.SysFont('comicsans', 30)
        label = font.render('Next Shape', 1, (255,255,255))

        sx = position + self.play_width + 50
        sy = self.top_left_y + self.play_height/2 - 100
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

        surface.blit(label, (sx + 10, sy- 30))


    def draw_lines_sent(self,surface, col,sx):

        sy = self.top_left_y
        for i in range(col):
            pygame.draw.line(surface, (128,128,128), (sx - 40, sy+ i*15 + self.play_height/2), (sx - 20, sy + i * 15 + self.play_height/2))   # horizontal lines

        pygame.draw.line(surface, (128,128,128), (sx - 40, sy + self.play_height/2), (sx - 40 , sy + self.play_height))  # vertical lines
        pygame.draw.line(surface, (128,128,128), (sx - 20, sy + self.play_height/2), (sx - 20 , sy + self.play_height))


    def draw_window(self,surface, label, position, grid, lines_sent):

        # Tetris Title

        surface.blit(label, (position + self.play_width / 2 - (label.get_width() / 2), 30))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (position + j* 30, self.top_left_y + i * 30, 30, 30), 0)

        # draw grid and border
        self.draw_grid(surface, 20, 10,position)
        for line in range(lines_sent):
            pygame.draw.rect(surface, (0,128,128), (position - 40, 685 - line * 15, 20, 15), 0)
        self.draw_lines_sent(surface, 20, position)
        pygame.draw.rect(surface, (255, 0, 0), (position, self.top_left_y, self.play_width, self.play_height), 5)

    def controls(self):
        rest = 9
        #move stuff

    def reset(self):
        pygame.display.set_caption('Tetris')
        self.screen = pygame.display.set_mode((self.s_width, self.s_height))
        self.locked_positions = {}  # (x,y):(255,0,0)
        self.locked_positions_human = {}
        font = pygame.font.SysFont('comicsans', 60)
        self.label_ai = font.render('AI Player', 1, (255, 255, 255))
        self.counter_ai = 0
        self.counter_human = 0
        self.bag_ai = self.get_shapes()
        self.change_piece = False
        self.win = False
        self.lose = False
        self.current_piece = self.bag_ai.pop()
        self.next_piece = self.bag_ai.pop()
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.score = 0

    def draw_stats(self):
        font = pygame.font.SysFont('comicsans', 30)

        label = font.render('Lines sent', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 50))
        label = font.render('Pieces placed', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y - 20))
        label = font.render('Score', 1, (255, 255, 255))
        self.screen.blit(label, (self.top_left_x + 400, self.top_left_y + 10))

    def score(self):
        return self.score


    def main(self, run=True):
        self.reset()
        while run:

            fall_speed = 0.27

            grid_ai = self.create_grid(self.locked_positions)
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()

            # PIECE FALLING CODE
            if self.fall_time/1000 >= fall_speed:
                ai_move = random.randint(0, 4)
                if ai_move == 0:
                    self.current_piece.x -= 1
                    if not self.valid_space(self.current_piece, grid_ai):
                        self.current_piece.x += 1
                elif ai_move == 1:
                    self.current_piece.x += 1
                    if not self.valid_space(self.current_piece, grid_ai):
                        self.current_piece.x -= 1
                elif ai_move == 2:
                    self.current_piece.rotation = self.current_piece.rotation + 1 % len(self.current_piece.shape)
                    if not self.valid_space(self.current_piece, grid_ai):
                        self.current_piece.x -= 1
                        if not self.valid_space(self.current_piece, grid_ai):
                            self.current_piece.x += 2
                            if not self.valid_space(self.current_piece, grid_ai):
                                self.current_piece.x += -1
                                self.current_piece.rotation = self.current_piece.rotation - 1 % len(
                                    self.current_piece.shape)
                self.fall_time = 0
                self.current_piece.y += 1
                if not (self.valid_space(self.current_piece, grid_ai)) and self.current_piece.y > 0:
                    self.current_piece.y -= 1
                    self.change_piece = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                    quit()

                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button.isover(pos):
                        print("Return")
                        run = False
                if event.type == pygame.MOUSEMOTION:
                    if self.return_button.isover(pos):
                        self.return_button.color = (61, 97, 128)
                    else:
                        self.return_button.color = (147, 150, 153)

            shape_pos = self.convert_shape_format(self.current_piece)
            # add piece to the grid for drawing
            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    grid_ai[y][x] = self.current_piece.color

            # IF PIECE HIT GROUND
            if self.change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    self.locked_positions[p] = self.current_piece.color
                self.current_piece = self.next_piece
                self.next_piece = self.bag_ai.pop()
                if not self.bag_ai:
                    self.bag_ai = self.get_shapes()
                self.change_piece = False

                # call four times to check for multiple clear rows
                self.counter_ai += self.clear_rows(grid_ai, self.locked_positions)
                self.score += self.counter_ai
                self.counter_ai = 0
                # Adds a row and moves rows up
                while self.counter_human > 0:
                    for j in range(10):
                        for i in range(20):
                            if (j,i) in self.locked_positions:
                                self.locked_positions[j,i-self.counter_human] = self.locked_positions[j,i]
                                del self.locked_positions[j,i]
                    lines_sent = random.sample(range(10), 9)
                    for x in range(self.counter_human):
                        for g in range(10):
                            self.locked_positions[g,19-x] = (0, 0, 0)
                    for x in range(self.counter_human):
                        for r in lines_sent:
                            self.locked_positions[r,19-x] = (169,169,169)
                    self.counter_human = 0

            self.screen.fill((0,0,0))
            self.draw_window(self.screen,self.label_ai,self.top_left_x,grid_ai, self.counter_human)
            self.draw_next_shape(self.next_piece, self.screen,self.top_left_x)
            self.return_button.draw(self.screen)
            self.draw_stats()
            pygame.display.update()

            # Check if user lost
            if self.check_lost(self.locked_positions_human):
                run = False
                self.lose = True
            if self.check_lost(self.locked_positions):
                run = False
                self.win = True

        if self.win:
            self.draw_text_middle("You Win", 40, (255,255,255), self.screen)
            pygame.display.update()
            pygame.time.delay(2000)
            self.main()
        if self.lose:
            self.draw_text_middle("You Lost", 40, (255,255,255), self.screen)
            pygame.display.update()
            pygame.time.delay(2000)
            self.main()

