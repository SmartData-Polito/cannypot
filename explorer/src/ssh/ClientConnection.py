from hosts import utils
from ssh.Channel import Channel
from twisted.conch.ssh import connection

class ClientConnection(connection.SSHConnection):

    def __init__(self, factory):
        self.factory = factory
        self.cmds = factory.cmds
        self.server = factory.host['address']
        connection.SSHConnection.__init__(self)
        self.factory.log.msg('[%s] connecting' % (self.factory.host['vm_name']))

    def serviceStarted(self):
        for cmd in self.cmds:
            self.factory.log.msg('[%s] sending command: %s' % (self.factory.host['vm_name'], cmd))
            self.openChannel(Channel(conn=self, cmd=cmd, server=self.server, factory=self.factory))

    def channelClosed(self, channel):
        self.factory.log.msg('[%s] closing connection' % (self.factory.host['vm_name']))
        connection.SSHConnection.channelClosed(self, channel)
