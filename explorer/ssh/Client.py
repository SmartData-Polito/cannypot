from twisted.internet import protocol, reactor

from config.ExplorerConfig import ExplorerConfig
from ssh.Transport import ClientTransport
import sys
from twisted.python import log
from twisted.internet import task

class ClientSSH:

    def __init__(self, cmds_list, hosts_list):
        self.cmds = cmds_list
        loop = task.LoopingCall(self.f)
        loop.start(5)
        log.startLogging(sys.stdout, setStdout=0)
        reactor.run()

    def f(self):
        factory = protocol.ClientFactory()
        factory.protocol = ClientTransport
        factory.cmds = self.cmds
        factory.server = ExplorerConfig().get('network', 'server')
        reactor.connectTCP(ExplorerConfig().get('network', 'server'), ExplorerConfig().getint('network', 'port'), factory)
