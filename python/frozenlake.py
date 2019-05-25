import gym
import numpy as np
import tensorflow as tf
from nn import *
import random

# hyperparams
EPISODES = 1000
memory = deque(maxlen=2000)
gamma = 0.95    # discount rate
epsilon = 1.0  # exploration rate
epsilon_min = 0.01
epsilon_decay = 0.995
learning_rate = 0.001
batch_size = 32

# state variables
done = False

# Initialize the game
env = gym.make('CartPole-v1')
state_size = env.observation_space.shape[0]
action_size = env.action_space.n

# init model
config = tf.ConfigProto()
config.gpu_options.allow_growth=True
session = tf.Session(config=config)
nn = NeuralNetwork("main", session, state_size,action_size, learning_rate)
nn = nn.build_model(2, [24, 24])

def remember(state, action, reward, next_state, done):
    memory.append((state, action, reward, next_state, done))

def act(state):
    if np.random.rand() <= epsilon:
        return random.randrange(action_size)
    act_values = predict(state)
    return np.argmax(act_values[0]) # returns action

def predict(state):
    return nn["output"].eval(feed_dict={nn["x"]: state})[0]

def replay(batch_size):
    global epsilon
    minibatch = random.sample(memory, batch_size)
    for state, action, reward, next_state, done in minibatch:
        target = reward
        if not done:
            target = (reward + gamma * np.amax(predict(next_state)[0]))
        target_f = [predict(state)]
        target_f[0][action] = target

        action_oh = np.zeros(action_size)
        action_oh[action] = 1

        session.run(nn["train"], feed_dict={
            nn["x"] : state,
            nn["action"] : [action_oh],
            nn["actual_q_value"] : target_f[0]
        })

    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

def main():
    with session.as_default():
        session.run(tf.global_variables_initializer())
        for e in range(EPISODES):
            state = env.reset()
        state = np.reshape(state, [1, state_size])
        for e in range(EPISODES):
            state = env.reset()
            state = np.reshape(state, [1, state_size])
            for time in range(500):
                #env.render()
                action = act(state)
                next_state, reward, done, _ = env.step(action)
                reward = reward if not done else -10
                next_state = np.reshape(next_state, [1, state_size])
                remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print("episode: {}/{}, score: {}, e: {:.2}".format(e, EPISODES, time, epsilon))
                    break
                if len(memory) > batch_size:
                    replay(batch_size)

main()