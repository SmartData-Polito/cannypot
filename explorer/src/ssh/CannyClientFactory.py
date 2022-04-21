import time
from twisted.internet import protocol

class CannyClientFactory(protocol.ClientFactory):

    def __init__(self, host, domain, cmds, log, explorer):
        protocol.ClientFactory.__init__(self)
        self.explorer = explorer
        self.host = host
        self.domain = domain
        self.config = explorer.config
        self.cmds = cmds.copy()
        self.log = log
        self.retry = 0
        self.log.msg("[%s] executing commands [%s]" % (host['vm_name'], cmds))

    def startedConnecting(self, connector):
        self.connector = connector

    def clientConnectionFailed(self, connector, reason):
        if self.retry < 5:
            self.log.msg("[%s] connection failed, will retry in 10s" % (self.host['vm_name']))
            time.sleep(10)
            self.retry += 1
            self.log.msg("[%s] retrying connection [%d]" % (self.host['vm_name'], self.retry))
            connector.connect()
        else:
            self.log.err("[%s] failed to connect" % (self.host['vm_name']))
            self.client_gone()

    def clientConnectionLost(self, connector, reason):
        self.log.msg("[%s] connection lost: %s" % (self.host['vm_name'], reason))

    def client_gone(self):
        self.log.msg("[%s] done. closing connection." % (self.host['vm_name']))
        try:
            self.connector.disconnect()
        except Exception as e:
            self.log.err(repr(e))
        self.explorer.vm_complete(self.host, self.domain)
