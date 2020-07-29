import argparse
import os
import shutil
from random import random, randint, sample
import pygame
import Button

import numpy as np
import torch
import torch.nn as nn
from tensorboardX import SummaryWriter

from DeepQLearning import DeepQNetwork
from TetrisCheater import Tetris as Cheater
from TetrisFair import Tetris as Fair
from collections import deque


def get_args(training_type):
    parser = argparse.ArgumentParser(
        """Implementation of Deep Q Network to play Tetris""")
    parser.add_argument("--width", type=int, default=10, help="The common width for all images")
    parser.add_argument("--height", type=int, default=20, help="The common height for all images")
    parser.add_argument("--block_size", type=int, default=30, help="Size of a block")
    parser.add_argument("--batch_size", type=int, default=512, help="The number of images per batch")
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--initial_epsilon", type=float, default=1)
    parser.add_argument("--final_epsilon", type=float, default=1e-3)
    parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--log_path", type=str, default="tensorboard")
    parser.add_argument("--save_interval", type=int, default=1000)

    if training_type == "cheater":
        parser.add_argument("--num_decay_epochs", type=float, default=2000)
        parser.add_argument("--num_epochs", type=int, default=3000)
        parser.add_argument("--replay_memory_size", type=int, default=30000,
                            help="Number of epoches between testing phases")

    elif training_type == "fair":
        parser.add_argument("--num_decay_epochs", type=float, default=3000)
        parser.add_argument("--num_epochs", type=int, default=5000)
        parser.add_argument("--replay_memory_size", type=int, default=100000,
                            help="Number of epoches between testing phases")

    args = parser.parse_args()
    return args


def train(opt, training_type, number_of_features):
    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if os.path.isdir(opt.log_path):
        shutil.rmtree(opt.log_path)
    os.makedirs(opt.log_path)
    writer = SummaryWriter(opt.log_path)
    screen = pygame.display.set_mode((1400, 700))
    if training_type == "fair":
        env = Fair(screen,"train",True)
    else:
        env = Cheater(screen,"train",True)
    model = DeepQNetwork(number_of_features)
    optimizer = torch.optim.Adam(model.parameters(), lr=opt.lr)
    criterion = nn.MSELoss()

    state = env.reset()
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()

    replay_memory = deque(maxlen=opt.replay_memory_size)
    epoch = 0
    max_steps = 2500
    steps = 0
    return_button = Button.Button((61, 97, 128), 575, 625, 200, 50, 'Return')
    while epoch < opt.num_epochs:
        next_steps = env.get_next_states()
        # Exploration or exploitation
        epsilon = opt.final_epsilon + (max(opt.num_decay_epochs - epoch, 0) * (
                opt.initial_epsilon - opt.final_epsilon) / opt.num_decay_epochs)
        u = random()
        random_action = u <= epsilon
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        if torch.cuda.is_available():
            next_states = next_states.cuda()
        model.eval()
        with torch.no_grad():
            predictions = model(next_states)[:, 0]
        model.train()
        if random_action:
            index = randint(0, len(next_steps) - 1)
        else:
            index = torch.argmax(predictions).item()

        next_state = next_states[index, :]
        action = next_actions[index]
        steps = steps + 1
        reward, done = env.step(action)

        if torch.cuda.is_available():
            next_state = next_state.cuda()
        replay_memory.append([state, reward, next_state, done])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if return_button.isover(pos):
                    writer.close()
                    return True
            if event.type == pygame.MOUSEMOTION:
                if return_button.isover(pos):
                    return_button.color = (61, 97, 128)
                else:
                    return_button.color = (147, 150, 153)
        return_button.draw(screen)
        pygame.display.update()
        if steps >= max_steps:
            done = True
        if done:
            steps = 0
            final_score = env.last_score
            final_tetrominoes = env.total_pieces_placed
            final_cleared_lines = env.total_lines_cleared
            max_combo = env.max_combo
            state = env.reset()
            if torch.cuda.is_available():
                state = state.cuda()
        else:
            state = next_state
            continue
        if len(replay_memory) < opt.replay_memory_size / 10:
            continue
        epoch += 1
        batch = sample(replay_memory, min(len(replay_memory), opt.batch_size))
        state_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        state_batch = torch.stack(tuple(state for state in state_batch))
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.stack(tuple(state for state in next_state_batch))

        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()

        q_values = model(state_batch)
        model.eval()
        with torch.no_grad():
            next_prediction_batch = model(next_state_batch)
        model.train()

        y_batch = torch.cat(
            tuple(reward if done else reward + opt.gamma * prediction for reward, done, prediction in
                  zip(reward_batch, done_batch, next_prediction_batch)))[:, None]

        optimizer.zero_grad()
        loss = criterion(q_values, y_batch)
        loss.backward()
        optimizer.step()

        print("Epoch: {}/{}, Action: {}, Score: {}, Tetrominoes {}, Cleared lines: {}, Max Combo: {}".format(
            epoch,
            opt.num_epochs,
            action,
            final_score,
            final_tetrominoes,
            final_cleared_lines,
            max_combo))
        writer.add_scalar('Train/Score', final_score, epoch - 1)
        writer.add_scalar('Train/Tetrominoes', final_tetrominoes, epoch - 1)
        writer.add_scalar('Train/Cleared lines', final_cleared_lines, epoch - 1)

        if epoch > 0 and epoch % opt.save_interval == 0:
            torch.save(model, "{}/{}_tetris_{}".format(opt.saved_path, training_type, epoch))

    torch.save(model, "{}/tetris".format(opt.saved_path))
    writer.close()


def main(training_type, number_of_features):
    opt = get_args(training_type)
    train(opt, training_type, number_of_features)
    return True
