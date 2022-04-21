import copy
from cowrie.learning.rl.cmd_parser import process_command
import base64


class LearningDictionary:

    def __init__(self, learningDict=None):

        # This is retrieved and stored in memory

        # Dictionary more faster than lists
        # command:parsed
        # These are all the known commands
        # Should I store them as hashes?
        self.known_commands = {
            #'unknown_command': 'unknown_command',
        }

        # Is it necessary to store the outputs as list here? If I have the hash I don't need to store the filenames
        # How to save data into qtable?
        self.outputs = {
            'unknown_command': ['CMD_not_found'],
        }

        if learningDict is not None:
            self.known_commands = copy.deepcopy(learningDict.known_commands)
            self.outputs = copy.deepcopy(learningDict.outputs)

    def getCommandList(self):
        return list(self.known_commands.keys())

    def getOutputsForCommand(self, command):
        return list(self.outputs[self.encodeCommand(command)])

    def isCommandInDict(self, command):
        return command in self.known_commands

    def isParsedCommandInDict(self, command):
        return process_command(command) in self.known_commands.values()

    def getParsedCommandInDict(self, complete_cmd):
        parsed = process_command(complete_cmd)
        match = None
        for key,value in self.known_commands.items():
            if parsed == value:
                print(complete_cmd, "<=====is equal to=====>", key)
                # If 1 match if found return that match 
                # Key is the command in dict, value is the parsed command dict 
                return key
        return None

    def getOutputByIndex(self, command, index):
        return self.outputs[self.encodeCommand(command)][index]

    def addCommandInDict(self, command):
        # when add command in dict is also directly add the corresponding parsed command
        self.known_commands[command] = process_command(command)
        # Maybe use the hash as index?
        self.outputs[self.encodeCommand(command)] = []

    def addOutputForCommand(self, command, output):
        encoded = self.encodeCommand(command)
        if output not in self.outputs[encoded]:
            self.outputs[encoded].append(output)

    def getNumOutputsForCommand(self, command):
        return len(self.getOutputsForCommand(command))

    def encodeCommand(self, command):
        return base64.b64encode(command.encode()).decode('utf-8')
    
    def decodeCommand(self, encoded):
        return base64.b64decode(encoded).decode('utf-8')
