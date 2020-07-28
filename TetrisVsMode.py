import pygame
import TetrisGameHuman
from Settings import Setting
import torch
import Button
from TetrisPlayFair import Tetris as Fair
from TetrisPlayCheater import Tetris as Cheater

# Default Settings
settings = Setting()
screen_width = settings.screen_width
screen_height = settings.screen_height
dark_grey = settings.screen_colour
screen_centre = screen_width/2
button_colour_off = settings.button_colour_off
button_colour_on = settings.button_colour_on
button_width = settings.button_width
button_height = settings.button_height
button_centred = screen_centre - button_width/2


def start(screen, saved_path="fair_tetris",mode="vs"):
    return_button = Button.Button(button_colour_off, 625, 625, 150, 50, 'Return')
    pygame.display.set_caption(saved_path)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if torch.cuda.is_available():
        model = torch.load("trained_models/{}".format(saved_path))
    else:
        model = torch.load("trained_models/{}".format(saved_path), map_location=lambda storage, loc: storage)
    model.eval()
    if saved_path == "fair_tetris":
        env = Fair(screen)
    else:
        env = Cheater(screen)
    env.reset()

    if torch.cuda.is_available():
        model.cuda()
    if mode == "vs":
        human_tetris = TetrisGameHuman.Tetris(screen)
        draw = False
    fall_time = 0
    fall_speed = 0.27
    clock = pygame.time.Clock()
    screen.fill((0, 0, 0))
    pygame.display.update()
    human_lines = 0
    holder = 0
    lost = False
    won = False
    run = True
    if mode == "vs":
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
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
                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if return_button.isover(pos):
                        return True
                if event.type == pygame.MOUSEMOTION:
                    if return_button.isover(pos):
                        return_button.color = (61, 97, 128)
                    else:
                        return_button.color = (147, 150, 153)
            if human_lines > 0:
                holder += human_lines
                human_lines = 0
            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                lost, human_lines = human_tetris.main(0)
                if human_lines > 0:
                    holder += human_lines
                    human_lines = 0
                reward, won = ai(env,model,holder,draw)
                holder = 0
                if reward > 0:
                    lost, human_lines = human_tetris.main(-1, reward)
                    if human_lines > 0:
                        holder += human_lines
                        human_lines = 0
            fall_time += clock.get_rawtime()
            clock.tick()
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
    else:
        draw = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if return_button.isover(pos):
                        return True
                if event.type == pygame.MOUSEMOTION:
                    if return_button.isover(pos):
                        return_button.color = (61, 97, 128)
                    else:
                        return_button.color = (147, 150, 153)
            reward, won = ai(env, model, holder,draw)
            return_button.draw(screen)
            pygame.display.flip()
            if won:
                env.reset()

    return True


def user_controls():
    red = ""

def ai(env,model,holder,draw):
    next_steps = env.get_next_states()
    next_actions, next_states = zip(*next_steps.items())
    next_states = torch.stack(next_states)
    if torch.cuda.is_available():
        next_states = next_states.cuda()
    predictions = model(next_states)[:, 0]
    index = torch.argmax(predictions).item()
    action = next_actions[index]
    reward, won = env.step(action, holder,draw)
    return reward, won


def gravity():
    red = ""


def display(win, lose, screen):
    pygame.draw.rect(screen, dark_grey, (1400 / 2 - 200, 200, 400, 300), 0)
    play_again_button = Button.Button(button_colour_off, 525, 300, 350, 50, 'Play Again?')
    selection_menu_button = Button.Button(button_colour_off, 525, 400, 350, 50, 'Selection Menu')
    if win:
        draw_text_middle("You Win", 40, (255, 255, 255), screen)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.isover(pos):
                        return True
                    elif selection_menu_button.isover(pos):
                        return False
                if event.type == pygame.MOUSEMOTION:
                    if play_again_button.isover(pos):
                        play_again_button.color = (61, 97, 128)
                    else:
                        play_again_button.color = (147, 150, 153)
                    if selection_menu_button.isover(pos):
                        selection_menu_button.color = (61, 97, 128)
                    else:
                        selection_menu_button.color = (147, 150, 153)
            play_again_button.draw(screen)
            selection_menu_button.draw(screen)
            pygame.display.update()
    if lose:
        draw_text_middle("You Lose", 40, (255, 255, 255), screen)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit()
                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.isover(pos):
                        return True
                    elif selection_menu_button.isover(pos):
                        return False
                if event.type == pygame.MOUSEMOTION:
                    if play_again_button.isover(pos):
                        play_again_button.color = (61, 97, 128)
                    else:
                        play_again_button.color = (147, 150, 153)
                    if selection_menu_button.isover(pos):
                        selection_menu_button.color = (61, 97, 128)
                    else:
                        selection_menu_button.color = (147, 150, 153)
            play_again_button.draw(screen)
            selection_menu_button.draw(screen)
            pygame.display.update()


def draw_text_middle(text, size, color, screen):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    screen.blit(label, (1400 / 2 - (label.get_width() / 2), 250 - label.get_height() / 2))
