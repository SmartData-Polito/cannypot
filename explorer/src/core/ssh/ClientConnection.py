from twisted.conch.ssh import connection
from ssh.Channel import Channel
from utils import utils


class ClientConnection(connection.SSHConnection):

    def __init__(self, cmds, server):
        self.cmds = cmds
        self.server = server
        connection.SSHConnection.__init__(self)

    def serviceStarted(self):
        for cmd in self.cmds:
            self.openChannel(Channel(conn=self, cmd=cmd, server=self.server))

    def channelClosed(self, channel):
        connection.SSHConnection.channelClosed(self, channel)
        if len(self.channels) == 0:
            utils.restore_vm_state(self.server)