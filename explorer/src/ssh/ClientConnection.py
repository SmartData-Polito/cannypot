import hashlib
from ssh.Terminal import Terminal
from twisted.conch.ssh import connection

class ClientConnection(connection.SSHConnection):

    def __init__(self, factory):
        self.factory = factory
        self.cmds = factory.cmds
        full_session = ";".join([i['complete_cmd'] for i in self.cmds])
        self.sessionid = hashlib.md5(full_session.encode('utf-8')).hexdigest()
        self.server = factory.host['vm_name'] + '--' + factory.host['address']
        connection.SSHConnection.__init__(self)
        self.factory.log.msg('[%s] connecting (session %s)' % (self.factory.host['vm_name'], self.sessionid))

    def serviceStarted(self):
        cmd = self.cmds[0]
        self.factory.log.msg('[%s] opening a new channel' % (self.factory.host['vm_name']))
        self.openChannel(Terminal(conn=self,
                                  cmd=cmd,
                                  server=self.server,
                                  factory=self.factory,
                                  sessionid=self.sessionid))
        del self.cmds[0]

    def channelClosed(self, channel):
        connection.SSHConnection.channelClosed(self, channel)
        if self.cmds:
            self.serviceStarted()
        else:
            self.factory.log.msg('[%s] closing connection' % (self.factory.host['vm_name']))
            self.factory.client_gone()
