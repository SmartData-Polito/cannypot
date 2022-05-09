import os
import json
import time
import base64
import struct
import hashlib
from tty_log import tty_utils
from twisted.internet import reactor
from twisted.conch.ssh import channel, common, session
from twisted.protocols.policies import TimeoutProtocol

TIMEOUT = 30 # time to wait for a command to finish (in s)

class Terminal(channel.SSHChannel):

    name = "session"

    def __init__(self, conn=None,
                        cmd=None,
                        server=None,
                        factory=None,
                        sessionid=None):
        self.cmd = cmd
        self.server = server
        self.factory = factory
        self.sessionid = sessionid
        self.ttylogFile = None
        self.received_data = b''
        self.output_dir = self.factory.config.output_dir
        self.json_dir = self.factory.config.json_dir

        self.timeout = None

        channel.SSHChannel.__init__(self, conn=conn)

    def channelOpen(self, data):
        self.factory.log.msg('[%s] opening channel ' % (self.factory.host['vm_name']))

        self.conn.transport.transport.setTcpNoDelay(1)

        term = os.environ.get('TERM', 'xterm')
        winSize = (25, 80, 0, 0)
        ptyReqData = session.packRequest_pty_req(term, winSize, '')
        d = self.conn.sendRequest(self, 'pty-req', ptyReqData, wantReply=True)
        d.addCallback(self.send_command)

    def send_command(self, ignored):
        self.cmd_hash = hashlib.md5(self.cmd['complete_cmd'].encode('utf-8')).hexdigest()
        self.factory.log.msg('[%s] command hash: %s  -- %s --) ' %
                            (self.factory.host['vm_name'], self.cmd_hash, self.cmd['complete_cmd']))


        os.makedirs(self.output_dir + self.cmd_hash, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        t = time.strftime("%Y%m%d_%H%M%S_%f")
        day = time.strftime("%Y%m%d")
        self.ttylogFile = self.output_dir + self.cmd_hash + '/ttylog_' + self.cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t
        self.ttyName = 'ttylog_' + self.cmd_hash + \
                          '_' + tty_utils.make_safe_filename(self.server) + '_' + t

        self.log_file = self.json_dir + self.factory.config.get('log', 'explorer_json_file') + '.' + day
        tty_utils.ttylog_open(self.ttylogFile, time.time())

        self.factory.log.msg('[%s] sending command: %s' % (self.factory.host['vm_name'], self.cmd))
        d = self.conn.sendRequest(self, 'exec', common.NS(self.cmd['complete_cmd']), wantReply=True)
        d.addCallback(self.send_eof)
        self.factory.log.msg('[%s] command sent' % (self.factory.host['vm_name']))

        with open(self.output_dir + self.cmd_hash + "/info.txt", 'w') as info:
            info.write(self.cmd['complete_cmd'] + "\n")
        with open(self.output_dir + self.cmd_hash + "/index.txt", 'a') as info:
            info.write(t + "\t")
            info.write(self.sessionid + "\t")
            info.write(self.factory.host['vm_name'] + "\t")
            info.write(self.ttyName + "\n")

    def send_eof(self, ignored):
        self.conn.sendEOF(self)
        self.factory.log.msg('[%s] eof sent' % (self.factory.host['vm_name']))
        self.timeout = reactor.callLater(TIMEOUT, self.abort)

    def abort(self):
        self.factory.log.msg('[%s] aborting' % (self.factory.host['vm_name']))
        self.timeout = None
        self.loseConnection()

    def dataReceived(self, data):
        self.received_data += data
        tty_utils.ttylog_write(self.ttylogFile, len(data), tty_utils.TYPE_OUTPUT, time.time(), data)
        # self.factory.log.msg('[%s] receiving data' % (self.factory.host['vm_name']))

    def request_exit_status(self, data):
        status = struct.unpack('>L', data)[0]
        self.factory.log.msg('[%s] request_exit_status' % (self.factory.host['vm_name']))
        j = {"eventid": "explorer.exec",
             "sessionid": str(self.sessionid),
             "exitcode": status,
             "cmd": base64.b64encode(self.cmd['complete_cmd'].encode()).decode('utf-8'),
             "cmd_hash": self.cmd_hash,
             "output": base64.b64encode(self.received_data).decode('utf-8'),
             "outputfile": self.ttyName,
             "machine": self.server,
             "timestamp": str(time.time())
        }

        with open(self.log_file,'a') as log_fp:
            log_fp.write(json.dumps(j))
            log_fp.write('\n')

    def extReceived(self, t, data):
        self.factory.log.msg('[%s] extReceived' % (self.factory.host['vm_name']))

    def request_exit_signal(self, data):
        self.factory.log.msg('[%s] request_exit_signal' % (self.factory.host['vm_name']))

    def eofReceived(self):
        self.factory.log.msg('[%s] eofReceived' % (self.factory.host['vm_name']))
        tty_utils.ttylog_close(self.ttylogFile, time.time())

    def closed(self):
        self.factory.log.msg('[%s] channel closed' % (self.factory.host['vm_name']))
        if self.timeout:
            self.timeout.cancel()
