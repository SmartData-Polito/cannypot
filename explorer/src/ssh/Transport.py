from twisted.conch.ssh import transport
from twisted.internet import defer
from ssh.ClientUserAuth import ClientUserAuth
from ssh.ClientConnection import ClientConnection
from hosts import utils


class ClientTransport(transport.SSHClientTransport):

    def verifyHostKey(self, pubKey, fingerprint):
        return defer.succeed(1)

    def connectionSecure(self):
        print("[DEBUG] 1. Connection secure")
        self.requestService(
          ClientUserAuth(self.factory.host['user'],
                         ClientConnection(self.factory),
                         self.factory.host['password']))
        print("[DEBUG] 2. Connection secure finish")

    def receiveError(self, reasonCode, description):
        print("[DEBUG] 1. Error received")
        self._log.error(
            "Got remote error, code {code}\nreason: {description}",
            code=reasonCode,
            description=description,
        )
        print("[DEBUG] 2. Restore vm after error received")
        utils.restore_vm_state(self.factory.server)
        print("[DEBUG] 3. Finish restore vm after error received")


