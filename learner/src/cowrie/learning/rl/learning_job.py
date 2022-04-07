from twisted.python import log
import numpy as np
import copy
from cowrie.core.config import CowrieConfig
import collections


class Job:

    def __init__(self):
        self.difference_table = {}
        self.new_commands = []
        self.commands_session = []
        self.episode_stats = {}
        self.qtable_updates = []

    def calculateDifferenceTable(self, initial_qtable, final_qtable):
        for state in list(final_qtable.keys()):
            if state not in initial_qtable.keys():
                self.difference_table[state] = np.zeros(len(final_qtable[state])).tolist()

    def insertNewCommands(self, new_commands_list):
        self.new_commands = new_commands_list

    def insertSessionCommands(self, commands_in_session_list):
        self.commands_session = commands_in_session_list

    def insertQtableUpdates(self, updates):
        self.qtable_updates = updates

    def getDifferenceTable(self):
        return self.difference_table

    def getNewCommands(self):
        return self.new_commands

    def getSessionCommands(self):
        return self.commands_session

    def insertEpisodeStats(self, episode_reward, steps, different_commands):
        self.episode_stats['episode_reward'] = episode_reward
        self.episode_stats['steps'] = steps
        self.episode_stats['different_commands'] = different_commands

    def getEpisodeStats(self):
        return self.episode_stats

    def getUpdates(self):
        return self.qtable_updates
