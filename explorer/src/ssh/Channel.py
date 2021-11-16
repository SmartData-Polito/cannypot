from twisted.conch.ssh import channel, common, session
import os
import time
from tty_log import tty_utils
import struct
from config.ExplorerConfig import ExplorerConfig
import json


class Channel(channel.SSHChannel):

    name = 'session'

    def __init__(self, conn=None, cmd=None, server=None):
        self.cmd = cmd
        self.server = server
        output_dir = ExplorerConfig().get('backend', 'output_dir')
        cmd_hash = str(hash(self.cmd['complete_cmd']))
        os.makedirs(output_dir+cmd_hash, exist_ok=True)
        t = time.strftime("%m:%d:%Y-%H:%M:%S")
        day = time.strftime("%Y%m%d")
        self.ttylogFile = output_dir+cmd_hash + '/ttylog_'+cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t
        self.ttyName = 'ttylog_'+cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t
        log_file_path = ExplorerConfig().get('log', 'explorer_json_file')
        self.log_file = log_file_path+'.'+day
        channel.SSHChannel.__init__(self, conn=conn)

    def channelOpen(self, data):
        print("[DEBUG] 1. Start opening channel")
        self.catData = b''
        tty_utils.ttylog_open(self.ttylogFile, time.time())
        term = os.environ.get('TERM', 'xterm')
        winSize = (25, 80, 0, 0)
        ptyReqData = session.packRequest_pty_req(term, winSize, '')
        self.conn.sendRequest(self, 'pty-req', ptyReqData, wantReply=1)
        d = self.conn.sendRequest(self, 'exec', common.NS(self.cmd['complete_cmd']),
                                  wantReply=1)
        d.addCallback(self._cbSendRequest)
        print("[DEBUG] 2. Channel open (?)")

    def _cbSendRequest(self, ignored):
        self.conn.sendEOF(self)

    def dataReceived(self, data):
        self.catData += data
        tty_utils.ttylog_write(self.ttylogFile,
                            len(data),
                            tty_utils.TYPE_INPUT,
                            time.time(),
                            data)

    def request_exit_status(self, data):
        status = struct.unpack('>L', data)[0]
        timestamp = time.strftime("%m:%d:%Y-%H:%M:%S")
        j = {"eventid": "explorer.exec", "exitcode": status, "cmd": self.cmd['complete_cmd'],
             "output": self.catData.decode('utf-8'), "outputfile": self.ttyName, "machine": self.server,
             "timestamp": timestamp}
        with open(self.log_file,'a') as log_fp:
            log_fp.write(json.dumps(j))
            log_fp.write('\n')


    def closed(self):
        self.loseConnection()
        cmd_hash = str(hash(self.cmd['complete_cmd']))
        if ExplorerConfig().getboolean('general', 'backup_outputs'):
            output_dir = ExplorerConfig().get('backend', 'output_dir')
            info_file = output_dir + cmd_hash + '/info.txt'
            if not os.path.exists(info_file):
                with open(info_file, "w") as file:
                    file.write(self.cmd['complete_cmd'])
                    file.close()
        else:
            os.remove(self.ttylogFile)

    def eofReceived(self):
        tty_utils.ttylog_close(self.ttylogFile, time.time())
        print(self.catData.decode('utf-8'))

