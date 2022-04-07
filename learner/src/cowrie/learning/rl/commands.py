import copy


class LearningDictionary:

    def __init__(self, learningDict=None):

        self.known_commands = [
            'ls'
        ]  # list of known commands
        # This is retrieved and stored in memory
        self.command_outputs = {
            'unknown_command': 'CMD_not_found',
            'ls': 'this_output'
        }
        self.outputs = {
            'CMD_not_found': ['CMD_not_found'],
            'this_output': ['this_exactly'],
        }

        if learningDict is not None:
            self.known_commands = copy.deepcopy(learningDict.known_commands)
            self.command_outputs = copy.deepcopy(learningDict.command_outputs)
            self.outputs = copy.deepcopy(learningDict.outputs)

    def getCommandList(self):
        return list(self.command_outputs.keys())

    def getOutputsForCommand(self, command):
        return list(self.outputs[self.command_outputs[command]])

    def isCommandInDict(self, command):
        return command in self.known_commands

    def getCommandOutput(self, command):
        return self.command_outputs[command]

    def getOutputByIndex(self, command, index):
        return self.outputs[self.command_outputs[command]][index]

    def addCommandInDict(self, command):
        self.known_commands.append(command)
        self.outputs[command] = []
        self.command_outputs[command] = command

    def addOutputForCommand(self, command, output):
        if output not in self.outputs[command]:
            self.outputs[command].append(output)

    def getNumOutputsForCommand(self, command):
        return len(self.getOutputsForCommand(command))
