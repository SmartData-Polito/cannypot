from twisted.internet import protocol



class CannyClientFactory(protocol.ClientFactory):

    def __init__(self, host, log):
        protocol.ClientFactory.__init__(self)
        self.cmds = cmds
        self.host= host
        self.log = log
        self.retry = 0
        self.log.msg(host['vm_name'], "executing commands", cmds)

    def buildProtocol(self):
        return ClientTransport()


    def clientConnectionFailed(self, connector, reason):
        if self.retry < 5:
            time.sleep(1)
            self.retry += 1
            self.log.msg(host['vm_name'], "connection failed, retry", self.retry)
            connector.connect()


# TODO What if something here fails? Should destroy vm!??
