from twisted.internet import protocol
import time


class CannyClientFactory(protocol.ClientFactory):

    def __init__(self, cmds, server, password):
        self.cmds = cmds
        self.server = server
        self.password = password
        protocol.ClientFactory.__init__(self)
        self.retry = 0

    def clientConnectionFailed(self, connector, reason):
        if self.retry < 5:
            time.sleep(1)
            self.retry += 1
            connector.connect()

    def clientConnectionLost(self, connector, reason):
        self.retry = 0

    def startedConnecting(self, connector):
        self.retry = 0