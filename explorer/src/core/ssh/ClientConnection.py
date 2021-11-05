from twisted.conch.ssh import connection
from ssh.Channel import Channel
from hosts import utils


class ClientConnection(connection.SSHConnection):

    def __init__(self, cmds, server):
        self.cmds = cmds
        self.server = server
        connection.SSHConnection.__init__(self)
        print("[DEBUG] ClientConnection init with cmds", cmds)

    def serviceStarted(self):
        print("[DEBUG] 1. Start service for all commands in file")
        for cmd in self.cmds:
            print("[DEBUG] Service started client connection for 1 command")
            self.openChannel(Channel(conn=self, cmd=cmd, server=self.server))

    def channelClosed(self, channel):
        print("[DEBUG] 1. Closing channel")
        connection.SSHConnection.channelClosed(self, channel)
        if len(self.channels) == 0:
            print("[DEBUG] 2. Starting restoring vm")
            utils.restore_vm_state(self.server)
            print("[DEBUG] 3. Finish restoring vm")
