from twisted.internet import defer
from twisted.conch.ssh import transport
from ssh.ClientUserAuth import ClientUserAuth
from ssh.ClientConnection import ClientConnection

class ClientTransport(transport.SSHClientTransport):

    def verifyHostKey(self, pubKey, fingerprint):
        self.factory.log.msg('[%s] SSH host fingerprinting' % (self.factory.host['vm_name']))
        return defer.succeed(1)

    def connectionSecure(self):
        self.factory.log.msg('[%s] SSH connection: %s:%s' %
                             (self.factory.host['vm_name'],
                              self.factory.host['address'],
                              self.factory.host['port']))
        self.requestService(
          ClientUserAuth(self.factory.host['user'],
                         ClientConnection(self.factory),
                         self.factory.host['password']))

    def receiveError(self, reasonCode, description):
        self.factory.log.err(
          "Got remote error, code {code}\nreason: {description}",
          code=reasonCode, description=description)
