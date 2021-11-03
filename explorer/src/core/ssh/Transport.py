from twisted.conch.ssh import transport
from twisted.internet import defer
from ssh.ClientUserAuth import ClientUserAuth
from ssh.ClientConnection import ClientConnection
from hosts import utils


class ClientTransport(transport.SSHClientTransport):

    def verifyHostKey(self, pubKey, fingerprint):
        return defer.succeed(1)

    def connectionSecure(self):
        self.requestService(ClientUserAuth('root', ClientConnection(self.factory.cmds, self.factory.server),
                                           self.factory.password))

    def receiveError(self, reasonCode, description):
        self._log.error(
            "Got remote error, code {code}\nreason: {description}",
            code=reasonCode,
            description=description,
        )
        utils.restore_vm_state(self.factory.server)
