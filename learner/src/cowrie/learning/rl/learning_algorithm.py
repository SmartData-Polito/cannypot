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


class CentralAlgorithm:
    '''
    Class to manage the central q-table of Cowrie. This class receives requests of q-table, it passes a copy of the current
    q-table and extracts from a queue of modifications the ones to use to modify the q-table. It also extracts the new commands
    to search for once the connection is ended
    '''

    def __init__(self, alg, learning_rate, discount, epsilon, evaluation):

        # Parameter for the learning algorithm
        self.ALG = alg
        self.LEARNING_RATE = learning_rate
        self.DISCOUNT = discount
        self.EPSILON = epsilon
        self.EVALUATION = evaluation
        self.exploration = True
        self.cumulative_reward = 0
        self.episode = 0
        self.runs = 0
        self.dict_update_period = int(CowrieConfig.get('dictionary', 'dict_update_frequency'))
        learning_state_file = CowrieConfig.get('learning', 'learning_state')
        try:
            self.loadLearningState(learning_state_file)
        except FileNotFoundError:
            self.q_table = {}
            self.command_dict = LearningDictionary()
        finally:
            # Queue for managing modifications of the q-table and new commands

            self.modification_queue = Queue()

            # Worker thread extracts from queue and works
            self.worker_queue = threading.Thread(target=self._handleAfterEpisodeTasks, args=(self.modification_queue,))
            self.worker_queue.setDaemon(True)
            self.worker_queue.start()
            self.lock = threading.Lock()
            self.lookForNewOutputs(self.command_dict)
            self.saveLearningState(learning_state_file, self.q_table, self.command_dict)

            if CowrieConfig.getboolean('learning', 'save_dict_and_q_table'):
                freq = CowrieConfig.getint('learning', 'save_dict_and_q_table_frequency')
                task.LoopingCall(self.save_dict_q_table).start(freq)

    def save_dict_q_table(self):
        output_dir = CowrieConfig.get('learning', 'output_dir')
        pathlib.Path(output_dir+'ckb/dictionary/').mkdir(parents=True, exist_ok=True)
        pathlib.Path(output_dir+'qtable/').mkdir(parents=True, exist_ok=True)
        dict_filename = '%sckb/dictionary/dict-%s.json' % (output_dir, time.strftime('%Y%m%d-%H%M%S'))
        q_table_filename = '%sqtable/q_table-%s.json' % (output_dir, time.strftime('%Y%m%d-%H%M%S'))
        with open(dict_filename, 'w') as file:
            json.dump(self.command_dict.outputs, file, indent=4)
        with open(q_table_filename, 'w') as file2:
            json.dump(self.q_table, file2, indent=4)

    def _handleJob(self, job):

        # Useful functions
        def _update(q_table, new_state, current_state, action, reward):
            if current_state is not None:
                max_future_q = np.max(q_table[new_state])
                current_q = q_table[current_state][action]
                new_q = (1 - self.LEARNING_RATE) * current_q + self.LEARNING_RATE * (
                        reward + self.DISCOUNT * max_future_q)
                q_table[current_state][action] = new_q

        def updateQTable(q_table, difference_table, updates):
            for state in list(difference_table.keys()):
                if state not in list(q_table.keys()):
                    q_table[state] = difference_table[state]
            for update in updates:
                _update(q_table, update['new_state'], update['current_state'], update['action'], update['reward'])

        def askForNewCommands(command_dict, new_command_list):
            new_commands_dir = CowrieConfig.get('dictionary', 'new_commands_dir')
            pathlib.Path(new_commands_dir).mkdir(exist_ok=True)
            if new_command_list:
                with open(new_commands_dir + 'new_commands_' + str(self.episode) + '.txt', 'w') as file:
                    for command in new_command_list:
                        if not command_dict.isCommandInDict(command):
                            cmd = command['command']
                            cmd += ' '
                            cmd += ' '.join(command['rargs'])
                            file.write(cmd+'\n')
                log.msg(eventid='cannypot.manager', input='new_commands_' + str(self.episode),
                        format='New unknown commands file created: %(input)s')

        def saveEpisodeStats(episodeStats):
            output_dir = CowrieConfig.get('learning', 'output_dir')
            pathlib.Path(output_dir).mkdir(exist_ok=True)
            self.cumulative_reward += episodeStats['episode_reward']
            if self.EVALUATION:
                if self.exploration:
                    output_filename = CowrieConfig.get('learning', 'output_filename')
                else:
                    output_filename = CowrieConfig.get('learning', 'eval_filename')
                self.exploration = not self.exploration
            else:
                output_filename = CowrieConfig.get('learning', 'output_filename')

            with open(output_filename, mode="a") as output_file:
                output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                output_writer.writerow([self.runs, self.episode, episodeStats['episode_reward'], self.cumulative_reward,
                                        episodeStats['steps'], episodeStats['different_commands']])

        # _handleJob function
        self.lock.acquire()
        try:
            if not self.EVALUATION or self.exploration is True:
                self.episode += 1
            # Update q-table with new values
            updateQTable(self.q_table, job.getDifferenceTable(), job.getUpdates())

            # Save the state of the q-table
            if CowrieConfig.getboolean('learning', 'save_state'):
                log.msg(eventid='cannypot.manager',
                        format='Saving learning state (dictionary and q-table)')
                learning_state_file = CowrieConfig.get('learning', 'learning_state')
                self.saveLearningState(learning_state_file, self.q_table, self.command_dict)

            # Discover new commands and write them into file.txt
            if CowrieConfig.getboolean('dictionary', 'ask_for_new_commands'):
                log.msg(eventid='cannypot.manager',
                        format='Writing file of unknown commands for the backend')
                askForNewCommands(self.command_dict, job.getNewCommands())

            # Check if new outputs are present to insert them into dictionary
            if CowrieConfig.getboolean('dictionary', 'look_for_new_outputs') \
                    and CowrieConfig.getint('dictionary', 'dict_update_frequency'):
                log.msg(eventid='cannypot.manager',
                        format='Looking for new outputs file')
                self.lookForNewOutputs(self.command_dict)

            # Save statistics of the episode and update counters
            if CowrieConfig.getboolean('learning', 'save_learning_stats'):
                log.msg(eventid='cannypot.manager',
                        format='Saving episode statistics')
                saveEpisodeStats(job.getEpisodeStats())

            # Reset for evaluating RL
            if self.episode == CowrieConfig.getint('learning', 'episodes_before_reset'):
                if CowrieConfig.getboolean('learning', 'reset_after_period'):
                    self.updateLearningParams()

        except Exception as e:
            log.err(eventid='cannypot.manager', format='Error in secondary thread: {}'.format(e))
        finally:
            self.lock.release()

    def _handleAfterEpisodeTasks(self, queue):
        while True:
            job = queue.get()
            self._handleJob(job)

    def getAlgInstance(self):
        self.lock.acquire()
        alg = ReinforcementAlg(alg=self.ALG, learning_rate=self.LEARNING_RATE, discount=self.DISCOUNT,
                               epsilon=self.EPSILON, q_table=copy.deepcopy(self.q_table),
                               command_dict=LearningDictionary(self.command_dict), exploration=self.exploration)
        self.lock.release()
        return alg

    def insertJobInQueue(self, job):
        self.modification_queue.put(job)

    def loadLearningState(self, inputFile):
        with open(inputFile, 'rb') as f:
            state_list = pickle.load(f)
            self.q_table = state_list[0]
            self.command_dict = state_list[1]

    def updateLearningParams(self):
        self.q_table.clear()
        self.command_dict = LearningDictionary()
        for command in self.command_dict.getCommandList():
            self.q_table[command] = np.zeros(len(self.command_dict.getOutputsForCommand(command)))
        self.episode = 0
        self.runs += 1
        self.cumulative_reward = 0

    def lookForNewOutputs(self, cmds_dict):
        new_outputs_dir = CowrieConfig.get('dictionary', 'new_outputs_dir')
        dict_dir_path = CowrieConfig.get('dictionary', 'dict_dir_path')
        pathlib.Path(new_outputs_dir).mkdir(exist_ok=True, parents=True)
        pathlib.Path(dict_dir_path).mkdir(exist_ok=True, parents=True)
        new_commands = os.listdir(new_outputs_dir)
        filtered_new_commands = [d for d in new_commands if time.time() - os.path.getmtime(new_outputs_dir+d) > 60]
        if filtered_new_commands:
            log.msg(eventid='cannypot.manager', input=str(new_commands),
                    format='New outputs files found: %(input)s')
        for new_cmd in filtered_new_commands:
            with open(new_outputs_dir + new_cmd + '/info.txt', 'r') as info_file:
                complete_cmd = info_file.readline().rstrip('\n')
                info_file.close()
            os.remove(new_outputs_dir + new_cmd + '/info.txt')
            if not cmds_dict.isCommandInDict(complete_cmd):
                cmds_dict.addCommandInDict(complete_cmd)
            for out_file in os.listdir(new_outputs_dir + new_cmd):
                if CowrieConfig.getint('dictionary', 'max_outputs_for_command') > cmds_dict.getNumOutputsForCommand(complete_cmd):
                    cmds_dict.addOutputForCommand(complete_cmd, out_file)
                    os.rename(new_outputs_dir + new_cmd + '/' + out_file, dict_dir_path + out_file)
                else:
                    os.remove(new_outputs_dir + new_cmd + '/' + out_file)
            os.rmdir(new_outputs_dir + new_cmd + '/')
            log.msg(eventid='cannypot.manager', input=str(new_cmd),
                    format='New outputs for cmd: %(input)s')

    def saveLearningState(self, outputFile, q_table, command_dict):
        state_dir = CowrieConfig.get('learning', 'learning_state_dir')
        pathlib.Path(state_dir).mkdir(exist_ok=True)
        with open(outputFile, 'wb') as f:
            pickle.dump([q_table, command_dict], f, pickle.HIGHEST_PROTOCOL)


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
