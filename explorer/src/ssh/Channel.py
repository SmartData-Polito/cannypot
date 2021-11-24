from twisted.conch.ssh import channel, common, session
from tty_log import tty_utils
import os
import json
import time
import struct
import hashlib

class Channel(channel.SSHChannel):

    name = "session"

    def __init__(self, conn=None, cmd=None, server=None, factory=None):
        self.cmd = cmd
        self.server = server
        self.factory = factory

        cmd_hash = hashlib.md5(self.cmd['complete_cmd'].encode('utf-8')).hexdigest()
        self.factory.log.msg('[%s] command hash: %s  -- %s --) ' %
                             (self.factory.host['vm_name'], cmd_hash, self.cmd['complete_cmd']))

        output_dir = self.factory.config.output_dir
        os.makedirs(output_dir + cmd_hash, exist_ok=True)
        t = time.strftime("%Y%m%d_%H%M%S")
        day = time.strftime("%Y%m%d")
        self.ttylogFile = output_dir + cmd_hash + '/ttylog_' + cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t
        self.ttyName = 'ttylog_' + cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t

        self.log_file = output_dir + self.factory.config.get('log', 'explorer_log_file') + '.' + day
        channel.SSHChannel.__init__(self, conn=conn)

    def channelOpen(self, data):
        self.factory.log.msg('[%s] opening channel ' % (self.factory.host['vm_name']))
        self.catData = b''
        tty_utils.ttylog_open(self.ttylogFile, time.time())

        #TODO: Here we should do better and format output
        term = os.environ.get('TERM', 'xterm')
        winSize = (25, 80, 0, 0)
        ptyReqData = session.packRequest_pty_req(term, winSize, '')
        self.conn.sendRequest(self, 'pty-req', ptyReqData, wantReply=1)
        d = self.conn.sendRequest(self, 'exec',
                                  common.NS(self.cmd['complete_cmd']), wantReply=1)
        d.addCallback(self._cbSendRequest)
        self.factory.log.msg('[%s] command sent' % (self.factory.host['vm_name']))
        #TODO: Save also the command on the TTY to make things simple.

    def _cbSendRequest(self, ignored):
        self.conn.sendEOF(self)

    def dataReceived(self, data):
        self.catData += data
        tty_utils.ttylog_write(self.ttylogFile,
                            len(data),
                            tty_utils.TYPE_INPUT,
                            time.time(),
                            data)
        self.factory.log.msg('[%s] receiving data' % (self.factory.host['vm_name']))

    def request_exit_status(self, data):
        status = struct.unpack('>L', data)[0]
        j = {"eventid": "explorer.exec", "exitcode": status, "cmd": self.cmd['complete_cmd'],
             "output": self.catData.decode('utf-8'), "outputfile": self.ttyName, "machine": self.server,
             "timestamp": str(time.time())}
        with open(self.log_file,'a') as log_fp:
            log_fp.write(json.dumps(j))
            log_fp.write('\n')

    def eofReceived(self):
        tty_utils.ttylog_close(self.ttylogFile, time.time())
        self.factory.log.msg('[%s] response received' % (self.factory.host['vm_name']))

    def closed(self):
        self.factory.log.msg('[%s] channel closed' % (self.factory.host['vm_name']))
