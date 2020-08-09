import pygame
import tetris_human
from settings import Setting
import torch
import button
from tetris_fair import Tetris as Fair
from tetris_cheater import Tetris as Cheater

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width / 2
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width / 2


def start(screen, saved_path="fair_tetris", mode="vs"):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    pygame.display.set_caption(saved_path)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)

    # Loads the model
    model = torch.load(("trained_models/{}".format(saved_path)), map_location=lambda storage, loc: storage).to(device)
    model.eval()

    screen.fill((0, 0, 0))
    if mode == "vs":
        human_tetris = tetris_human.Tetris(screen)
        draw = False
    else:
        draw = True
    if saved_path == "fair_tetris":
        env = Fair(screen, "play", draw)
    else:
        env = Cheater(screen, "play", draw)
    env.reset()

    pygame.display.update()
    font_small = pygame.font.SysFont('Arial', 20)
    return_button = button.Button(button_colour_off, 625, 625, 150, 50, 'Return')
    # Runs vs mode or solo mode
    if mode == "vs":
        vs_mode(return_button, env, model, screen, human_tetris)
    else:
        solo_mode(return_button, env, model, screen, font_small)

    return True


def vs_mode(return_button, env, model, screen, human_tetris):
    speed_1 = button.Button(button_colour_on, 610, 25, 30, 30, '1x', 1)
    speed_2 = button.Button(button_colour_off, 650, 25, 30, 30, '2x', 2)
    speed_3 = button.Button(button_colour_off, 690, 25, 30, 30, '3x', 3)
    buttons = [speed_1, speed_2, speed_3]
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    ai_speed = 0
    lost = False
    won = False
    run = True
    speed = 1
    human_lines = 0
    holder = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            # User controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    lost, human_lines = human_tetris.main(1)
                elif event.key == pygame.K_RIGHT:
                    lost, human_lines = human_tetris.main(2)
                elif event.key == pygame.K_UP:
                    lost, human_lines = human_tetris.main(3)
                elif event.key == pygame.K_DOWN:
                    lost, human_lines = human_tetris.main(4)
                elif event.key == pygame.K_SPACE:
                    lost, human_lines = human_tetris.main(5)
                elif event.key == pygame.K_LSHIFT:
                    lost, human_lines = human_tetris.main(6)
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.is_over(pos):
                    return True
            if event.type == pygame.MOUSEMOTION:
                if return_button.is_over(pos):
                    return_button.color = (61, 97, 128)
                else:
                    return_button.color = (147, 150, 153)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for x in range(len(buttons)):
                    if buttons[x].is_over(pos):
                        speed = buttons[x].value
                    buttons[x].color = button_colour_off
                buttons[speed - 1].color = button_colour_on
        if human_lines > 0:
            holder += human_lines
            human_lines = 0
        if holder > 0:
            env.lines(holder)
            holder = 0
        if (ai_speed / 2000) * speed >= fall_speed:
            reward, won = ai(env, model, holder)
            holder = 0
            if reward > 0:
                lost, human_lines = human_tetris.main(-1, reward)
                if human_lines > 0:
                    holder += human_lines
                    human_lines = 0
            ai_speed = 0
        if fall_time / 1000 >= fall_speed:
            lost, human_lines = human_tetris.main(0)
            if human_lines > 0:
                holder += human_lines
                human_lines = 0
            fall_time = 0
        fall_time += clock.get_rawtime()
        ai_speed += clock.get_rawtime()
        clock.tick()
        for x in range(len(buttons)):
            buttons[x].draw(screen)
        return_button.draw(screen)
        pygame.display.update()

        if won or lost:
            return_button.color = (0, 0, 0)
            return_button.draw(screen)
            run = display(won, lost, screen)
            screen.fill((0, 0, 0))
            env.reset()
            human_tetris.reset()
            lost = False
            won = False


# Solo mode
def solo_mode(return_button, env, model, screen, font_small):
    clock = pygame.time.Clock()
    area = pygame.Rect(0, 75, 900, 625)
    holder = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.is_over(pos):
                    return True
            if event.type == pygame.MOUSEMOTION:
                if return_button.is_over(pos):
                    return_button.color = (61, 97, 128)
                else:
                    return_button.color = (147, 150, 153)
        reward, won = ai(env, model, holder)
        return_button.draw(screen)
        fps = font_small.render("fps:" + str(int(clock.get_fps())), True, pygame.Color('white'))
        screen.blit(fps, (10, 75))
        clock.tick(200)
        pygame.display.update(area)
        if won:
            env.reset()


# Controls Agent
def ai(env, model, holder):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    next_steps = env.get_next_states()
    next_actions, next_states = zip(*next_steps.items())
    next_states = torch.stack(next_states).to(device)

    predictions = model(next_states)[:, 0]
    index = torch.argmax(predictions).item()
    action = next_actions[index]
    reward, won = env.step(action, holder)
    return reward, won


# End game display
def display(win, lose, screen):
    pygame.draw.rect(screen, dark_grey, (1400 / 2 - 200, 200, 400, 300), 0)
    play_again_button = button.Button(button_colour_off, 525, 300, 350, 50, 'Play Again?')
    selection_menu_button = button.Button(button_colour_off, 525, 400, 350, 50, 'Selection Menu')
    if win and lose:
        end_text = "Draw"
    elif win:
        end_text = "You Win"
    else:
        end_text = "You Lose"
    draw_text_middle(end_text, 40, (255, 255, 255), screen)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.is_over(pos):
                    return True
                elif selection_menu_button.is_over(pos):
                    return False
            if event.type == pygame.MOUSEMOTION:
                if play_again_button.is_over(pos):
                    play_again_button.color = (61, 97, 128)
                else:
                    play_again_button.color = (147, 150, 153)
                if selection_menu_button.is_over(pos):
                    selection_menu_button.color = (61, 97, 128)
                else:
                    selection_menu_button.color = (147, 150, 153)
        play_again_button.draw(screen)
        selection_menu_button.draw(screen)
        pygame.display.update()


# Draws centred text
def draw_text_middle(text, size, color, screen):
    font = pygame.font.SysFont('Arial', size, bold=True)
    label = font.render(text, 1, color)

    screen.blit(label, (1400 / 2 - (label.get_width() / 2), 250 - label.get_height() / 2))
