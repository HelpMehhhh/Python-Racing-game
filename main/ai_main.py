import os
from cars import AiCar
import random as r
import cProfile
import torch
import pickle
import numpy as np
from graphics import Graphics


from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(12, 256, 6)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = r.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_outputs = [0,0,0,0,0,0]
        if r.randint(0, 200) < self.epsilon:
            steer = r.randint(0, 2)
            speed = r.randint(3, 5)
            final_outputs[steer] = 1
            final_outputs[speed] = 1
        
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            prediction.reshape(2,3)
            final_outputs[torch.argmax(prediction[0]).item()] = 1
            final_outputs[(torch.argmax(prediction[1]).item())+3] = 1

        return final_outputs


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    with open(os.path.join(os.path.dirname(__file__), 'center_points_08.pickle'), 'rb') as f: cent_line = pickle.load(f)
    ai_car = AiCar(0, 0, [0,0], 1, 14, 21, cent_line)
    graphics = Graphics(ai_car)
    while True:
        # get old state
        state_old = ai_car.get_data()

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = ai_car.tick(17, final_move, 0)
        state_new = ai_car.get_data()

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        graphics.graphics_loop(ai_car)
        if done:
            # train long memory, plot result
            ai_car.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
        

if __name__ == '__main__':
    train()


