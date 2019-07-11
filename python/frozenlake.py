# -*- coding: utf-8 -*-
import random
import gym
import tensorflow as tf
import numpy as np
from collections import deque
from nn import *

EPISODES = 300

config = tf.ConfigProto()
config.gpu_options.allow_growth=True
session = tf.Session(config=config)

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=1000)
        self.gamma = 0.99    # discount rate
        self.epsilon = 0.5  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.0001
        self.train_start = 100
        self.iterations = 0
        self.model = NeuralNetwork("main", session, state_size,action_size, self.learning_rate)
        self.target_model = NeuralNetwork("target", session, state_size,action_size, self.learning_rate)
        self.model.build_model(1, [20])#, 24])
        self.target_model.build_model(1, [20])#, 24])
        self.t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='main')
        self.e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='target')

        self.replace_target_op = [tf.assign(t, e) for t, e in zip(self.t_params, self.e_params)]

    def predict(self, state):
        return self.get_map()["output"].eval(feed_dict={self.get_map()["x"]: state})

    def predict_target(self, state):
        return self.target_model.get_map()["output"].eval(feed_dict={self.target_model.get_map()["x"]: state})

    def get_map(self):
        return self.model.get_map()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        global epsilon
        if len(self.memory) < self.train_start:
            return

        minibatch = random.sample(self.memory, batch_size)
        states = [x[0][0] for x in minibatch]
        actions = []
        rewards = [x[2] for x in minibatch]
        next_states = [x[3][0] for x in minibatch]
        y_batch = []

        qvals = self.predict(next_states)
        i = 0
        for state, action, reward, next_state, done in minibatch:
            if done:
                y_batch.append(rewards[i])
            else:
                y_batch.append(rewards[i] + self.gamma * np.amax(qvals[i]))

            action_oh = np.zeros(action_size)
            action_oh[action] = 1
            actions.append(action_oh)
            i = i + 1

        session.run(self.get_map()["train"], feed_dict={
            self.get_map()["x"] : states,
            self.get_map()["action"] : actions,
            self.get_map()["actual_q_value"] : y_batch
        })

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    env = gym.make('CartPole-v1')
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)

    with session.as_default():
        session.run(tf.global_variables_initializer())
        session.run(agent.replace_target_op)
        # agent.load("./save/cartpole-dqn.h5")
        done = False
        batch_size = 32

        for e in range(EPISODES):
            state = env.reset()
            state = np.reshape(state, [1, state_size])
            #session.run(agent.replace_target_op)

            for time in range(500):
                #env.render()
                action = agent.act(state)
                next_state, reward, done, _ = env.step(action)
                reward = reward if not done else -10
                next_state = np.reshape(next_state, [1, state_size])
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print("episode: {}/{}, score: {}, e: {:.2}"
                          .format(e, EPISODES, time, agent.epsilon))
                    break
                if len(agent.memory) > batch_size:
                    agent.replay(batch_size)

                agent.iterations = agent.iterations + 1
            # if e % 10 == 0:
            #     agent.save("./save/cartpole-dqn.h5")