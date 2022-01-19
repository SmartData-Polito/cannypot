from ssh.Terminal import Terminal
from twisted.conch.ssh import connection

class ClientConnection(connection.SSHConnection):

    def __init__(self, factory):
        self.factory = factory
        self.cmds = factory.cmds
        self.server = factory.host['address']
        connection.SSHConnection.__init__(self)
        self.factory.log.msg('[%s] connecting' % (self.factory.host['vm_name']))

    def serviceStarted(self):
        cmd = self.cmds[0]
        self.factory.log.msg('[%s] opening a new channel' % (self.factory.host['vm_name']))
        self.openChannel(Terminal(conn=self, cmd=cmd, server=self.server, factory=self.factory))
        del self.cmds[0]

    def channelClosed(self, channel):
        connection.SSHConnection.channelClosed(self, channel)
        if self.cmds:
            self.serviceStarted()
        else:
            self.factory.log.msg('[%s] closing connection' % (self.factory.host['vm_name']))
            self.factory.client_gone()
