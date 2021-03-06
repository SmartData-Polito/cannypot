from twisted.python import log
import numpy as np
from multiprocessing import Queue
import threading
import copy
import csv
import pickle
import os
import json
import shutil
import hashlib
import time
from cowrie.learning.rl.commands import LearningDictionary
from cowrie.learning.rl.algorithm_instance import ReinforcementAlg
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
        #self.dict_update_period = int(CowrieConfig.get('dictionary', 'dict_update_frequency'))  # TODO what's the purpose of this variable if it is never used?
        learning_state_file = CowrieConfig.get('learning', 'learning_state')

        # Initialize them also before the try catch
        self.q_table = {}
        self.command_dict = LearningDictionary()

        if not self.loadLearningState(learning_state_file):
            self.q_table = {}
            self.command_dict = LearningDictionary()

            
        # Queue for managing modifications of the q-table and new commands
        #log.msg("Command dictionary is", self.command_dict)

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
        #dict_filename = '%sckb/dictionary/dict-%s.json' % (output_dir, time.strftime('%Y%m%d-%H%M%S'))
        # Update dict while saving history of qtable
        dict_filename = '%sckb/dictionary/dict.json'  % (output_dir)
        q_table_filename = '%sqtable/q_table-%s.json' % (output_dir, time.strftime('%Y%m%d-%H%M%S'))
        log.msg("Saving dict and qtable")
        with open(dict_filename, 'w') as file:
            log.msg("Len command_dict.outputs", len(self.command_dict.outputs))
            json.dump(self.command_dict.outputs, file, indent=4)
        with open(q_table_filename, 'w') as file2:
            log.msg("Len qtable", len(self.q_table))
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

        def askForNewCommands(command_dict, new_command_list, commands_in_session_list):
            # commands_in_session_list = the entire session, so IF new command list, save the entire session
            log.msg("Saving unknown commands")
            log.msg("New commands list:", new_command_list)
            log.msg("All commands in session:", commands_in_session_list)
            new_commands_dir = CowrieConfig.get('dictionary', 'new_commands_dir')
            #print(next(os.walk(new_commands_dir), (None, None, []))[2])
            pathlib.Path(new_commands_dir).mkdir(exist_ok=True)

            # TODO could consider parser here (or before)

            # Save the entire session if unknown commands are present
            if new_command_list:
                # Generate filename hashing the entire session (;)
                full_session = ";".join(commands_in_session_list)
                filename = new_commands_dir + hashlib.md5(full_session.encode('utf-8')).hexdigest()

                # Check if file already exists
                if os.path.exists(filename):
                    log.msg(eventid='cannypot.manager', input=filename,
                            format='New unknown session file already exists: %(input)s. Not saving duplicated session')
                else: 
                    # If not exist, write the file joining commands with \n
                    with open(filename, 'w') as file:
                        file.write("\n".join(commands_in_session_list))
                        file.write("\n")
                    log.msg(eventid='cannypot.manager', input=filename,
                            format='New unknown session file created: %(input)s')

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
                log.msg("Job new commands:", job.getNewCommands())
                log.msg("Job episode statistics:", job.getEpisodeStats())

                askForNewCommands(self.command_dict, job.getNewCommands(), job.getSessionCommands())

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

    def loadState(self, inputFile):
        with open(inputFile, 'rb') as f:
            state_list = pickle.load(f)
            log.msg("Reading saved state file")
            log.msg(state_list)
            self.q_table = state_list[0]
            self.command_dict = state_list[1] 


    def loadLearningState(self, inputFile):
        backup_tried = False
        try: 
            if pathlib.Path(inputFile).is_file():
                self.loadState(inputFile)
                return True
            elif pathlib.Path(inputFile+".backup").is_file():
                log.msg("Saved state file not found. Trying to load backup file")
                backup_tried = True
                self.loadState(inputFile+".backup")
                return True
        except EOFError as e:
            if backup_tried:
                log.msg("EOFError in loadLearningState while loading backup file")
            else: 
                log.msg("EOFError in loadLearningState. Trying to load backup file")
                try:
                    self.loadState(inputFile+".backup")
                    return True
                except EOFError as e:
                    return False
        return False
                

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
        new_explorer_files = os.listdir(new_outputs_dir)

        # The name of the file is computed in Terminal.py in the Explorer has:
        # self.cmd_hash = hashlib.md5(self.cmd['complete_cmd'].encode('utf-8')).hexdigest()

        filtered_hash_commands = [d for d in new_explorer_files]
        if filtered_hash_commands:
            log.msg(eventid='cannypot.manager', input=str(filtered_hash_commands),
                    format='New outputs files found: %(input)s')

        for hash_cmd in filtered_hash_commands:
            with open(new_outputs_dir + hash_cmd + '/info.txt', 'r') as info_file:
                complete_cmd = info_file.readline().rstrip('\n')
                info_file.close()
            if not cmds_dict.isCommandInDict(complete_cmd):
                cmds_dict.addCommandInDict(complete_cmd)
                pathlib.Path(dict_dir_path + hash_cmd).mkdir(exist_ok=True)
                # Check if info.txt and index.txt exist and in case move them
                if os.path.isfile(new_outputs_dir + hash_cmd + '/info.txt'):
                    os.replace(new_outputs_dir + hash_cmd + '/info.txt', dict_dir_path + hash_cmd + '/info.txt')  # I am keeping info.txt because could be useful
                if os.path.isfile(new_outputs_dir + hash_cmd + '/index.txt'):
                    os.replace(new_outputs_dir + hash_cmd + '/index.txt', dict_dir_path + hash_cmd + '/index.txt')  # I am keeping index.txt because could be useful
            for out_file in os.listdir(new_outputs_dir + hash_cmd):
                if out_file == 'info.txt' or out_file == 'index.txt':
                    continue
                # TODO It could check here if empty or if it is the same as the other outputs!!
                if CowrieConfig.getint('dictionary', 'max_outputs_for_command') > cmds_dict.getNumOutputsForCommand(complete_cmd):
                    cmds_dict.addOutputForCommand(complete_cmd, out_file)
                    # On Unix, if src is a file and dst are both files, dst it will be replaced silently if the user has permission
                    os.rename(new_outputs_dir + hash_cmd + '/' + out_file, dict_dir_path + hash_cmd + '/' + out_file)
                else:
                    # Extra outputs are simply removed and not taken into account!
                    # TODO Maybe this could be changed, maybe put updated outputs/random outputs
                    # TODO what about random comamnds
                    os.remove(new_outputs_dir + hash_cmd + '/' + out_file)
            # Remove the directory with all outputs for the same command compute by the explorer
            os.rmdir(new_outputs_dir + hash_cmd + '/')
            log.msg(eventid='cannypot.manager', input=str(hash_cmd),
                    format='New outputs for cmd: %(input)s')

    def saveLearningState(self, outputFile, q_table, command_dict):
        # Adding a backup system in order to recover if the honeypot breaks while saving the learning state
        state_dir = CowrieConfig.get('learning', 'learning_state_dir')
        # TODO check what's saved here and if it is saved correctly: for now seems to be
        log.msg("Saving state")
        pathlib.Path(state_dir).mkdir(exist_ok=True)

        if pathlib.Path(outputFile).is_file():
            #if file already exists:
            # temporarily store in another overwriting
            # force overwrite
            shutil.copy(outputFile, outputFile + '.backup')
            # If dst is a directory, a file is created (or overwritten)

        with open(outputFile, 'wb') as f:
            pickle.dump([q_table, command_dict], f, pickle.HIGHEST_PROTOCOL)