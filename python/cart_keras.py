# -*- coding: utf-8 -*-
import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

EPISODES = 1000

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        states, targets_f = [], []
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            # Filtering out states and targets for training
            states.append(state[0])
            targets_f.append(target_f[0])
        history = self.model.fit(np.array(states), np.array(targets_f), epochs=1, verbose=0)
        # Keeping track of loss
        loss = history.history['loss'][0]
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return loss

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    env = gym.make('CartPole-v1')
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)
    # agent.load("./save/cartpole-dqn.h5")
    done = False
    batch_size = 32

    for e in range(EPISODES):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        for time in range(500):
            # env.render()
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            reward = reward if not done else -10
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            loss = 0
            if len(agent.memory) > batch_size:
                loss = agent.replay(batch_size)
            if done:
                print("episode: {}/{}, score: {}, loss: {}, e: {:.2}"
                      .format(e, EPISODES, time, loss, agent.epsilon))
                break

"""
episode: 0/1000, score: 36, loss: 2.033647060394287, e: 0.98
episode: 1/1000, score: 41, loss: 1.8614808320999146, e: 0.79
episode: 2/1000, score: 80, loss: 2.5632143020629883, e: 0.53
episode: 3/1000, score: 60, loss: 1.0715980529785156, e: 0.39
episode: 4/1000, score: 104, loss: 0.8617762923240662, e: 0.23
episode: 5/1000, score: 31, loss: 0.35747289657592773, e: 0.2
episode: 6/1000, score: 16, loss: 1.6762055158615112, e: 0.18
episode: 7/1000, score: 39, loss: 8.466679573059082, e: 0.15
episode: 8/1000, score: 72, loss: 26.064208984375, e: 0.1
episode: 9/1000, score: 165, loss: 0.3012640178203583, e: 0.044
episode: 10/1000, score: 332, loss: 0.06786945462226868, e: 0.01
episode: 11/1000, score: 252, loss: 0.1098066046833992, e: 0.01
episode: 12/1000, score: 102, loss: 28.94289779663086, e: 0.01
episode: 13/1000, score: 168, loss: 0.12261655926704407, e: 0.01
episode: 14/1000, score: 113, loss: 0.1081317663192749, e: 0.01
episode: 15/1000, score: 97, loss: 9.768539428710938, e: 0.01
episode: 16/1000, score: 111, loss: 0.1278144121170044, e: 0.01
episode: 17/1000, score: 138, loss: 8.290574073791504, e: 0.01
episode: 18/1000, score: 105, loss: 0.10409928113222122, e: 0.01
episode: 19/1000, score: 94, loss: 11.721243858337402, e: 0.01
episode: 20/1000, score: 111, loss: 0.15777422487735748, e: 0.01
episode: 21/1000, score: 114, loss: 0.06954111158847809, e: 0.01
episode: 22/1000, score: 122, loss: 0.10382276773452759, e: 0.01
episode: 23/1000, score: 164, loss: 0.04481598362326622, e: 0.01
episode: 24/1000, score: 123, loss: 0.0731305181980133, e: 0.01
episode: 25/1000, score: 159, loss: 0.08740118145942688, e: 0.01
"""