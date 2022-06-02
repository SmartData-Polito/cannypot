import struct
import time
from twisted.internet import reactor
from twisted.python import failure
from twisted.internet import error
from cowrie.core.config import CowrieConfig

from twisted.python import log
import hashlib


OP_OPEN, OP_CLOSE, OP_WRITE, OP_EXEC = 1, 2, 3, 4
TYPE_INPUT, TYPE_OUTPUT, TYPE_INTERACT = 1, 2, 3


class HoneypotTerminalEmulator:

    def __init__(self, honeypot):
        self.honeypot = honeypot

    def run_command(self, complete_cmd):
        if complete_cmd == 'exit' or complete_cmd == 'Exit':
            log.msg("Honeypot terminal emulator exiting")
            # updates = self.honeypot.protocol.learning_env.connection_closed()
            # self.honeypot.protocol.user.avatar.learning_handler.episode_finished(updates)
            stat = failure.Failure(error.ProcessDone(status=""))
            self.honeypot.protocol.terminal.transport.processEnded(stat)
        else:
            log.msg("Honeypot terminal emulator receiving command:", complete_cmd)
            output = self.honeypot.protocol.learning_env.command_received(complete_cmd)

            # Here it is the filename, so I should add the hashlib.md5(complete_cmd.encode('utf-8')).hexdigest() of the complete_cmd
            output_file = hashlib.md5(complete_cmd.encode('utf-8')).hexdigest() + "/" + output.strip()
            reactor.callInThread(self._playlog, output_file)

    def _playlog(self, out_filename):
        ssize = struct.calcsize('<iLiiLL')
        currtty, prevtime, prefdir = 0, 0, 0

        stdout = self.honeypot.protocol.terminal
        dict_dir_path = CowrieConfig.get('dictionary', 'dict_dir_path')
        try:
            with open(dict_dir_path + out_filename, 'rb') as fd:
                log.msg(eventid='cannypot.learning.output',
                        format='Possible output file found')
                while 1:
                    try:
                        (op, tty, length, dir, sec, usec) = \
                            struct.unpack('<iLiiLL', fd.read(ssize))
                        data = fd.read(length)
                    except struct.error:
                        break

                    if currtty == 0:
                        currtty = tty

                    if str(tty) == str(currtty) and op == OP_WRITE:
                        # the first stream seen is considered 'output'
                        if prefdir == 0:
                            prefdir = dir
                            # use the other direction
                        if dir == TYPE_INTERACT:
                            color = b'\033[36m'
                        elif dir == TYPE_INPUT:
                            color = b'\033[33m'
                        if dir == prefdir:
                            curtime = float(sec) + float(usec) / 1000000
                            if prevtime != 0:
                                sleeptime = curtime - prevtime
                                time.sleep(sleeptime)
                            prevtime = curtime
                            reactor.callFromThread(stdout.write, data)
                    elif str(tty) == str(currtty) and op == OP_CLOSE:
                        break
                reactor.callFromThread(self.honeypot.runOrPrompt)
        except FileNotFoundError:
            log.msg("File not found: " + dict_dir_path + out_filename + ". Not doing anything")
            reactor.callFromThread(self.honeypot.runOrPrompt)