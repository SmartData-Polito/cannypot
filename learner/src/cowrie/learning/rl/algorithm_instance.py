from twisted.python import log
import numpy as np
from multiprocessing import Queue
import threading
import copy
import csv
import pickle
import os
import json
import time
from cowrie.learning.rl.commands import LearningDictionary
from cowrie.core.config import CowrieConfig
import pathlib
from twisted.internet import task


class ReinforcementAlg:
    '''
    Instance class, which is a copy of the learning algorithm. It initializes the q-table using the one given
    by the central algorithm, it modifies it and then it passes the modified q-table back to the central algorithm,
    which will manage the modifications to the q-table.
    It allows to work in parallel with multiple users - cowrie manages multiple connections in parallel.
    '''
    def __init__(self, alg, learning_rate, discount, epsilon, q_table, command_dict, exploration=True):
        self.ALG = alg
        self.LEARNING_RATE = learning_rate
        self.DISCOUNT = discount
        self.INITIAL_EPSILON = epsilon
        self.EPSILON = epsilon
        self.EXPLORATION = exploration
        self.initial_q_table = copy.deepcopy(q_table)
        self.q_table = q_table
        self.command_dict = command_dict
        self.already_seen_commands = []
        self.unknown_commands = []
        self.qtable_updates = []

        self.step = 0
        self.different_commands_seq = 0
        self.episode_reward = 0
        self.previous_state = None
        self.current_state = None
        self.previous_action = None

    def _get_reward_for_step(self, curr_attacker_state):
        if curr_attacker_state == 'Exit':
            reward = -1
        else:
            reward = 1
        return reward

    def _update(self, alg, new_state, current_state, action, reward):
        if current_state is not None:
            if alg == 'Q-Learning':
                max_future_q = np.max(self.q_table[new_state])
                log.msg(eventid='cannypot.learning', max_future_q=float(max_future_q), step=self.step,
                        format='Step %(step)i - Max future q: %(max_future_q)f')
                current_q = self.q_table[current_state][action]
                log.msg(eventid='cannypot.learning', current_q=float(current_q), step=self.step,
                        format='Step %(step)i - current q: %(current_q)f')
                new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (
                        reward + self.DISCOUNT * max_future_q)
                log.msg(eventid='cannypot.learning', new_q=float(new_q), step=self.step,
                        format='Step %(step)i - New q: %(new_q)f')
                self.q_table[current_state][action] = new_q
                update = {'new_state': new_state,
                          'current_state': current_state,
                          'action': action,
                          'reward': reward}
                self.qtable_updates.append(update)

    def produce_output(self, state):
        log.msg(eventid='cannypot.learning', state=str(state), step=self.step,
                format='Step %(step)i - Q-Learning in state: %(state)s')
        self.previous_state = self.current_state
        self.current_state = state
        if np.random.uniform(0, 1) < self.EPSILON and self.EXPLORATION:
            action = np.random.randint(0, len(self.q_table[self.current_state]))
            log.msg(eventid='cannypot.learning', step=self.step, action=int(action), exploration=1,
                    format='Step %(step)i - EXPLORATION Action chosen: %(action)i')
        else:
            action = np.argmax(self.q_table[self.current_state])
            log.msg(eventid='cannypot.learning', step=self.step, action=int(action), exploration=0,
                    format='Step %(step)i - EXPLOITATION Action chosen: %(action)i')

        reward = self._get_reward_for_step(self.current_state)
        log.msg(eventid='cannypot.learning', reward=reward, step=self.step,
                format='Step %(step)i - Reward: %(reward)i')
        self.episode_reward += reward
        if self.EXPLORATION:
            self._update(self.ALG, self.current_state, self.previous_state, self.previous_action, reward)
        self.step += 1
        self.previous_action = action
        return action

    def attacker_exited(self, exit_state):
        self._update(self.ALG, exit_state, self.current_state, self.previous_action, -1)
        self.already_seen_commands.clear()
        return self.q_table, self.episode_reward, self.step
