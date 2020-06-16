import pygame
import sys
import Button
import TetrisGame

pygame.init()

size = width, height = 450, 600
speed = [1, 1]
black = 71, 73, 74

screen = pygame.display.set_mode(size)


train_ai_button = Button.Button((61, 97, 128), 100, 100, 250, 100, 'Train AI')
play_vs_ai_button = Button.Button((61, 97, 128), 100, 250, 250, 100, 'Play Vs AI')
quit_button = Button.Button((61, 97, 128), 100, 400, 250, 100, 'Quit')

mode = 0
while 1:
    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT: sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if train_ai_button.isover(pos):
                print("Train AI")
                mode = 1
            if play_vs_ai_button.isover(pos):
                print("Play vs AI")
                TetrisGame.main()
                size = width, height = 450, 600
                screen = pygame.display.set_mode(size)
            if quit_button.isover(pos):
                print("Quit")
                sys.exit()
        if event.type == pygame.MOUSEMOTION:
            if train_ai_button.isover(pos):
                train_ai_button.color = (61, 97, 128)
            else:
                train_ai_button.color = (147, 150, 153)
            if play_vs_ai_button.isover(pos):
                play_vs_ai_button.color = (61, 97, 128)
            else:
                play_vs_ai_button.color = (147, 150, 153)
            if quit_button.isover(pos):
                quit_button.color = (61, 97, 128)
            else:
                quit_button.color = (147, 150, 153)

    screen.fill(black)
    train_ai_button.draw(screen)
    play_vs_ai_button.draw(screen)
    quit_button.draw(screen)
    pygame.display.update()
    if mode == 1:
        size = width, height = 1200, 600
        screen = pygame.display.set_mode(size)
        return_button = Button.Button((61, 97, 128), 975, 525, 200, 50, 'Return')
    while mode == 1:

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT: sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.isover(pos):
                    print("Return")
                    mode = 0
                    size = width, height = 450, 600
                    screen = pygame.display.set_mode(size)
            if event.type == pygame.MOUSEMOTION:
                if return_button.isover(pos):
                    return_button.color = (61, 97, 128)
                else:
                    return_button.color = (147, 150, 153)
        screen.fill(black)
        return_button.draw(screen)
        pygame.display.update()
