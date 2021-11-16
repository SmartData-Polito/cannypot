from twisted.internet import protocol
import time

class CannyClientFactory(protocol.ClientFactory):

    def __init__(self, host, cmds, log):
        protocol.ClientFactory.__init__(self)
        self.cmds = cmds
        self.host= host
        self.log = log
        self.retry = 0
        self.log.msg("[%s] executing commands [%s]" % (host['vm_name'], cmds))

    def clientConnectionFailed(self, connector, reason):
        if self.retry < 5:
            self.log.msg("[%s] connection failed, will retry in 10s" % (host['vm_name']))
            time.sleep(10)
            self.retry += 1
            self.log.msg()
            self.log.msg("[%s] retrying connection [%d]" % (host['vm_name'], self.retry))
            connector.connect()
