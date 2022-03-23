from twisted.python import log
import numpy as np
import copy
from cowrie.core.config import CowrieConfig
from cowrie.learning.rl.learning_job import Job
import collections


class LearningEnv:
    learning_alg = None

    def __init__(self):
        max_len = CowrieConfig.getint('learning', 'num_entry_states')
        state_model = CowrieConfig.get('learning', 'reinforcement_state')
        if state_model == 'multiple_out':
            max_len = max_len*2
        if max_len > 1 and state_model == 'single':
            max_len = 1
        elif max_len <= 1 and state_model != 'single':
            max_len = 3  # put default value for max_len to 3
        self.state_array = collections.deque(maxlen=max_len)
        self.commands_received = []
        self.unknown_commands = []
        self.commands_found = 0

    def init_learning_alg(self, alg):
        self.learning_alg = alg
        self.initial_qtable = copy.deepcopy(alg.q_table)
        log.msg(eventid='cannypot.manager', format="Reinforcement learning logic for the session initialized")
        log.msg(eventid='cannypot.learning.episode', format='RL episode started')

    def command_received(self, command, args):

        def produce_state(state_arr):
            state_model = CowrieConfig.get('learning', 'reinforcement_state')
            if state_model == 'single':
                return state_arr[-1]
            else:
                return '#'.join(self.state_array)

        def insert_cmd_out(state_array, entry, out=False):
            state_model = CowrieConfig.get('learning', 'reinforcement_state')
            if state_model == 'single' or state_model == 'multiple':
                if not out:
                    state_array.append(entry)
            else:
                state_array.append(entry)
            return state_array

        '''
        Arrived new command. If the state is known forwards the state to the learning
        alg, otherwise create a new state and then forwards to the learning module.

        :param command: command sent by the attacker
        :return: output from the learning module
        '''

        # Generate a complete commands starting from cmd and args
        complete_cmd = command
        for arg in args:
            complete_cmd += ' '
            complete_cmd += arg
        log.msg(eventid='cannypot.learning.input', input=complete_cmd, format='RL received command: %(input)s')

        # Check if inside dictionary we know one output for the command
        if not self.learning_alg.command_dict.isCommandInDict(complete_cmd):
            complete_cmd = 'unknown_command'
        else:
            log.msg(eventid='cannypot.learning.input.success', known=1, input=complete_cmd, format='RL known command: %(input)s')
        if complete_cmd not in self.state_array:
            self.commands_found += 1
            self.commands_received.append(complete_cmd)
        self.state_array = insert_cmd_out(self.state_array, complete_cmd, False)
        # Find the state starting from the list of commands received
        # and check if the state is already present in the q-table, otherwise the state is added
        state = produce_state(self.state_array)
        if state not in self.learning_alg.q_table:
            self.learning_alg.q_table[state] = \
                np.zeros(len(self.learning_alg.command_dict.getOutputsForCommand(complete_cmd))).tolist()
        # Send the state to the algorithm and select the output
        action = self.learning_alg.produce_output(state)
        output = self.learning_alg.command_dict.getOutputByIndex(complete_cmd, action)
        log.msg(eventid='cannypot.learning.output', output=str(output), input=str(complete_cmd),
                format='Output corresponding to action: %(output)s')
        self.state_array = insert_cmd_out(self.state_array, output, True)
        return output+'\n'

    def connection_closed(self):
        '''
        The connection with the attacker is closed (clean exit)


        '''
        self.state_array.append('exit')

        # Find the state starting from the list of commands received
        # and check if the state is already present in the q-table, otherwise the state is added
        state = '#'.join(self.state_array)
        if state not in self.learning_alg.q_table:
            self.learning_alg.q_table[state] = [0]
        q_table, ep_reward, steps = self.learning_alg.attacker_exited(state)
        log.msg(eventid='cannypot.learning.episode', reward=str(ep_reward), format='RL episode finished. Reward: %(reward)s')

        log.msg("Connection closed normally. Starting job in the environment")
        job = Job()
        job.calculateDifferenceTable(self.initial_qtable, q_table)
        job.insertNewCommands(self.unknown_commands)
        job.insertEpisodeStats(episode_reward=ep_reward, steps=steps,
                               different_commands=self.commands_found)
        job.insertQtableUpdates(self.learning_alg.qtable_updates)
        return job

    def connection_closed_dirty(self):
        '''
        The connection with the attacker is closed 
        '''
        self.state_array.append('exit')

        # Find the state starting from the list of commands received
        # and check if the state is already present in the q-table, otherwise the state is added
        state = '#'.join(self.state_array)
        if state not in self.learning_alg.q_table:
            self.learning_alg.q_table[state] = [0]
        q_table, ep_reward, steps = self.learning_alg.attacker_exited(state)
        log.msg(eventid='cannypot.learning.episode', reward=str(ep_reward), format='RL episode finished. Reward: %(reward)s')

        log.msg("Connection closed dirty. Starting job in the environment")
        job = Job()
        job.calculateDifferenceTable(self.initial_qtable, q_table)
        job.insertNewCommands(self.unknown_commands)
        job.insertEpisodeStats(episode_reward=ep_reward, steps=steps,
                               different_commands=self.commands_found)
        job.insertQtableUpdates(self.learning_alg.qtable_updates)

        return job
