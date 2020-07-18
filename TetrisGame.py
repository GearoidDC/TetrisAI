import pygame
import random
import Button

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

# GLOBALS VARS
s_width = 1400
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30

top_left_x = (s_width - play_width) // 5
top_right_x = (s_width - play_width) // 1.3
top_left_y = s_height - play_height


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
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # number from 0-3


def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
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


def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 0:
            return True
    return False


def get_shapes():
    global shapes, shape_colors
    bar = random.sample(range(0, 7), 7)
    bag = []
    for i in range(7):
        bag.append(Piece(5, 0, shapes[bar[i]]))

    return bag


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (s_width/2 - (label.get_width() / 2), top_left_y - label.get_height()/2))


def draw_grid(surface, row, col, sx):
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines


def clear_rows(grid, locked):
    # need to see if row is clear the shift every other row above down one
    linessss = 0
    i = len(grid)-1
    while i > 0:
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
                print(inc)
                for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                    x, y = key
                    if y < ind:
                        newKey = (x, y + 1)
                        locked[newKey] = locked.pop(key)
                        grid = create_grid(locked)
        else:
            i = i - 1
    return linessss


def draw_next_shape(shape, surface,position):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255,255,255))

    sx = position + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy- 30))


def draw_lines_sent(surface, col,sx):

    sy = top_left_y
    for i in range(col):
        pygame.draw.line(surface, (128,128,128), (sx - 40, sy+ i*15 + play_height/2), (sx - 20, sy + i * 15 + play_height/2))   # horizontal lines

    pygame.draw.line(surface, (128,128,128), (sx - 40, sy + play_height/2), (sx - 40 , sy + play_height))  # vertical lines
    pygame.draw.line(surface, (128,128,128), (sx - 20, sy + play_height/2), (sx - 20 , sy + play_height))


def draw_window(surface, label, position, grid, lines_sent):

    # Tetris Title

    surface.blit(label, (position + play_width / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (position + j* 30, top_left_y + i * 30, 30, 30), 0)

    # draw grid and border
    draw_grid(surface, 20, 10,position)
    for line in range(lines_sent):
        pygame.draw.rect(surface, (0,128,128), (position - 40, 685 - line * 15, 20, 15), 0)
    draw_lines_sent(surface, 20, position)
    pygame.draw.rect(surface, (255, 0, 0), (position, top_left_y, play_width, play_height), 5)
    # pygame.display.update()


def main():
    pygame.display.set_caption('Tetris')
    screen = pygame.display.set_mode((s_width, s_height))
    locked_positions = {}  # (x,y):(255,0,0)
    locked_positions_human = {}
    font = pygame.font.SysFont('comicsans', 60)
    label_ai = font.render('AI Player', 1, (255,255,255))
    label_human = font.render('Human Player', 1, (255,255,255))
    counter_ai = 0
    counter_human = 0
    bag_ai = get_shapes()
    bag_human = get_shapes()
    change_piece = False
    change_piece_human = False
    run = True
    win = False
    lose = False
    current_piece = bag_ai.pop()
    next_piece = bag_ai.pop()
    current_piece_human = bag_human.pop()
    next_piece_human = bag_human.pop()
    clock = pygame.time.Clock()
    fall_time = 0
    while run:

        fall_speed = 0.27

        grid_ai = create_grid(locked_positions)
        grid_human = create_grid(locked_positions_human)
        fall_time += clock.get_rawtime()
        clock.tick()

        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            ai_move = random.randint(0, 4)
            if ai_move == 0:
                current_piece.x -= 1
                if not valid_space(current_piece, grid_ai):
                    current_piece.x += 1
            elif ai_move == 1:
                current_piece.x += 1
                if not valid_space(current_piece, grid_ai):
                    current_piece.x -= 1
            elif ai_move == 2:
                current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                if not valid_space(current_piece, grid_ai):
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid_ai):
                        current_piece.x += 2
                        if not valid_space(current_piece, grid_ai):
                            current_piece.x += -1
                            current_piece.rotation = current_piece.rotation - 1 % len(
                                current_piece.shape)
            fall_time = 0
            current_piece.y += 1
            current_piece_human.y += 1
            if not (valid_space(current_piece, grid_ai)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
            if not (valid_space(current_piece_human, grid_human)) and current_piece_human.y > 0:
                current_piece_human.y -= 1
                change_piece_human = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece_human.x -= 1
                    if not valid_space(current_piece_human, grid_human):
                        current_piece_human.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece_human.x += 1
                    if not valid_space(current_piece_human, grid_human):
                        current_piece_human.x -= 1
                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece_human.rotation = current_piece_human.rotation + 1 % len(current_piece_human.shape)
                    if not valid_space(current_piece_human, grid_human):
                        current_piece_human.x -= 1
                        if not valid_space(current_piece_human, grid_human):
                            current_piece_human.x += 2
                            if not valid_space(current_piece_human, grid_human):
                                current_piece_human.x += -1
                                current_piece_human.rotation = current_piece_human.rotation - 1 % len(current_piece_human.shape)

                if event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece_human.y += 1
                    if not valid_space(current_piece_human, grid_human):
                        current_piece_human.y -= 1

                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece_human, grid_human):
                        current_piece_human.y += 1
                    current_piece_human.y -= 1
                    print(convert_shape_format(current_piece_human))

            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.isover(pos):
                    print("Return")
                    run = False
            if event.type == pygame.MOUSEMOTION:
                if return_button.isover(pos):
                    return_button.color = (61, 97, 128)
                else:
                    return_button.color = (147, 150, 153)

        shape_pos = convert_shape_format(current_piece)
        shape_pos_human = convert_shape_format(current_piece_human)
        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid_ai[y][x] = current_piece.color
        for i in range(len(shape_pos_human)):
            x, y = shape_pos_human[i]
            if y > -1:
                grid_human[y][x] = current_piece_human.color

        # IF PIECE HIT GROUND
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = bag_ai.pop()
            if not bag_ai:
                bag_ai = get_shapes()
            change_piece = False

            # call four times to check for multiple clear rows
            counter_ai += clear_rows(grid_ai, locked_positions)
            # Adds a row and moves rows up
            while counter_human > 0:
                for j in range(10):
                    for i in range(20):
                        if (j,i) in locked_positions:
                            locked_positions[j,i-counter_human] = locked_positions[j,i]
                            del locked_positions[j,i]
                lines_sent = random.sample(range(10), 9)
                for x in range(counter_human):
                    for g in range(10):
                        locked_positions[g,19-x] = (0, 0, 0)
                for x in range(counter_human):
                    for r in lines_sent:
                        locked_positions[r,19-x] = (169,169,169)
                counter_human = 0
        if change_piece_human:
            for pos in shape_pos_human:
                p = (pos[0], pos[1])
                locked_positions_human[p] = current_piece_human.color
            current_piece_human = next_piece_human
            next_piece_human = bag_human.pop()
            if not bag_human:
                bag_human = get_shapes()
            change_piece_human = False

            # call four times to check for multiple clear rows
            counter_human += clear_rows(grid_human, locked_positions_human)
            # Adds a row and moves rows up
            while counter_ai > 0:
                counter_ai = counter_ai - 1
                for j in range(10):
                    for i in range(20):
                        if (j,i) in locked_positions_human:
                            locked_positions_human[j,i-1] = locked_positions_human[j,i]
                            del locked_positions_human[j,i]
                lines_sent = random.sample(range(10), 9)
                for g in range(10):
                    locked_positions_human[g,19] = (0, 0, 0)
                for r in lines_sent:
                    locked_positions_human[r,19] = (169,169,169)

        screen.fill((0,0,0))
        draw_window(screen,label_ai,top_left_x,grid_ai, counter_human)
        draw_window(screen,label_human,top_right_x,grid_human, counter_ai)
        draw_next_shape(next_piece, screen,top_left_x)
        draw_next_shape(next_piece_human, screen,top_right_x)
        return_button.draw(screen)
        pygame.display.update()

        # Check if user lost
        if check_lost(locked_positions_human):
            run = False
            lose = True
        if check_lost(locked_positions):
            run = False
            win = True

    if win:
        draw_text_middle("You Win", 40, (255,255,255), screen)
        pygame.display.update()
        pygame.time.delay(2000)
        main()
    if lose:
        draw_text_middle("You Lost", 40, (255,255,255), screen)
        pygame.display.update()
        pygame.time.delay(2000)
        main()